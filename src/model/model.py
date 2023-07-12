import logging
import os
from typing import final, List, Dict, Union, Optional
from builtins import property
from pathlib import Path
import pandas as pd
import networkx as nx

from model.ocel.base import OCEL, DummyEventLog
from model.ocel.ocpa import OcpaEventLog, OCPA_DEFAULT_SETTINGS
from model.ocel.pm4py import Pm4pyEventLog
from model.constants import *
import pm4py

OCEL_CONSTRUCTORS = {
    BACKEND_OCPA: OcpaEventLog,
    BACKEND_PM4PY: Pm4pyEventLog,
    BACKEND_DUMMY: DummyEventLog
}

logger = logging.getLogger("app_logger")


class Model:

    def __init__(self, dataset):
        """
        The list self.ocels saves one or more OCEL objects (e.g. one Pm4pyEventLog and one OcpaEventLog).
        When accessing a model method, the corresponding OCEL method is called on the OCELs in the order as they are saved in the list.
        Caching is used to completely omit duplicate method calls on the OCEL objects.
        """
        self._ocels = []  # originally filtered_ocel
        self.original_ocel: OCEL = None

        self.active_ot = []
        self.active_activities = []
        self.filter_timestamp = None

        self.dataset = dataset
        self.result_cache: dict = {}
        self.ocels_traverse_extensions = [
            self.duplicate_first_to_ocpa,
            None
        ]

    def init_ocel(self, dataset, backend=BACKEND_PM4PY):
        event_log_constructor = OCEL_CONSTRUCTORS[backend]
        logger.info(f"Loading OCEL from file ({backend}) ...")
        ocel = event_log_constructor(self, **dataset)
        if len(self._ocels) == 0:
            self.original_ocel = ocel
        self._ocels.append(ocel)

        self.active_ot = self.object_types
        self.active_activities = self.activities
        logger.info(f"OCEL loaded successfully ({backend})")

    def update_active_ot_in_model(self, active_ot):
        self.active_ot = active_ot
        self.filter_ocel()

    def update_active_activities_in_model(self, active_activities):
        self.active_activities = active_activities
        self.filter_ocel()

    def update_timestamp_filter(self, start, end):
        self.filter_timestamp = (start, end)
        self.filter_ocel()

    def filter_ocel(self):
        """
        Applies filters on the event log. Duplicate event log instances are deleted, only retaining one pm4py instance.
        Merged all filters to one function:
            - timestamp
            - object types
            - activities
        """
        if not isinstance(self.original_ocel, Pm4pyEventLog):
            raise NotImplementedError("Filtering is only supported for pm4py event logs.")
        ocel = self.original_ocel.ocel

        # Timestamp
        # if self.filter_timestamp is not None:
        #     start, end = self.filter_timestamp
        #     if start is None:
        #         start = ocel.events['ocel:timestamp'].min()
        #     if end is None:
        #         end = ocel.events['ocel:timestamp'].max()
        #     ocel = pm4py.filter_ocel_events_timestamp(ocel, start, end)

        # Object types and activities
        if self.active_ot and self.active_activities:
            # example for desired dictionary: {“order”: [“Create Order”], “element”: [“Create Order”, “Create Delivery”]}
            ot_activity_dict = self.original_ocel.ot_activities
            active_ot_activity_filter_dict = {}
            for ot in self.active_ot:
                active_ot_activity_filter_dict[ot] = []
                for activity in self.active_activities:
                    if activity in ot_activity_dict[ot]:
                        active_ot_activity_filter_dict[ot].append(activity)

            ocel = pm4py.filter_ocel_object_types_allowed_activities(ocel, active_ot_activity_filter_dict)

        # save filtered event log and delete cache
        self._ocels = [Pm4pyEventLog(self, ocel=ocel)]
        self.reset_cache()

    def duplicate_first_to_ocpa(self):
        """
        Reduces the self.ocels list to the first entry (assume Pm4pyEventLog), then exports this event log to a file
        and imports it as an OcpaEventLog, saving it as the second entry in self.ocels
        """
        logger.info("Reading the filtered OCEL with ocpa module")
        target_file = 'tmp.jsonocel'
        target_path = Path("../data/datasets") / target_file
        pm4py_ocel = self._ocels[0]
        self._ocels = [pm4py_ocel]
        pm4py_ocel.export_json_ocel(target_path)
        self.init_ocel(dataset={"dataset": target_file, **{k: v for k, v in self.dataset.items() if k != "dataset"}},
                       backend=BACKEND_OCPA,
                       )
        os.remove(target_path)
        return True

    def _execute_ocel_method(self, method_name, *args):
        """
        Manages multiple OCEL wrapper instances, with caching.
        :param method_name: The name of the method to be called on an OCEL wrapper instance
        :param *args: Further args. Must be hashable.
        """

        if args:
            args_key = tuple(args)
        if self.result_cache.get(method_name, None) is not None:
            if args:
                if args_key in self.result_cache[method_name]:
                    return self.result_cache[method_name][args_key]
            else:
                return self.result_cache[method_name]

        logger.info(f"Request '{method_name}' (not in cache)")
        i = 0
        while i < len(self._ocels):
            method = getattr(self._ocels[i], method_name)
            result = method(*args)
            if result is not None:
                if args:
                    if method_name not in self.result_cache:
                        self.result_cache[method_name] = {}
                    self.result_cache[method_name][args_key] = result
                else:
                    self.result_cache[method_name] = result
                return result

            # Extend OCEL list? (copy pm4py log to ocpa)
            if len(self._ocels) == i + 1 and self.ocels_traverse_extensions[i] is not None:
                logger.info("Extend OCEL list ...")
                extended = self.ocels_traverse_extensions[i]()
                if not extended:
                    break

            i += 1

        raise NotImplementedError("The model's event log(s) do not support the requested method.")

    @property
    @final
    def object_types(self) -> List[str]:
        return self._execute_ocel_method("_get_object_types")

    @property
    @final
    def object_type_counts(self) -> List[str]:
        return self._execute_ocel_method("_get_object_type_counts")

    @property
    @final
    def activities(self) -> List[str]:
        return self._execute_ocel_method("_get_activities")

    @property
    @final
    def ot_activities(self) -> List[str]:
        return self._execute_ocel_method("_get_ot_activities")

    @property
    @final
    def cases(self) -> List[str]:
        return self._execute_ocel_method("_get_cases")

    @property
    @final
    def variants(self) -> List[str]:
        return self._execute_ocel_method("_get_variants")

    @property
    @final
    def variant_frequencies(self) -> Dict[str, int]:
        return self._execute_ocel_method("_get_variant_frequencies")

    @final
    def variant_graph(self, variant_id):
        return self._execute_ocel_method("_get_variant_graph", variant_id)

    @final
    def compute_opera(self, agg: Union[List[str], str, None] = None) -> Optional[Dict[str, Dict[str, pd.DataFrame]]]:
        dfs = self._execute_ocel_method("_compute_opera", agg)
        return dfs

    @final
    def compute_petri_net(self):
        return self._execute_ocel_method("_compute_petri_net")

    @final
    def compute_heatmap(self):
        return self._execute_ocel_method("_compute_heatmap")

    @final
    @property
    def extended_table(self):
        return self._execute_ocel_method("_get_extended_table")

    @final
    def compute_heatmap_pooling(self):
        return self._execute_ocel_method("_compute_heatmap_pooling")
    
    @final
    def compute_heatmap_lagging(self):
        return self._execute_ocel_method("_compute_heatmap_lagging")
    
    def reset_cache(self) -> None:
        """
        When any event log changes are made, this function is called.
        """
        self.result_cache = {}
        

