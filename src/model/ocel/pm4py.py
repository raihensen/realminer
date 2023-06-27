from typing import Dict

import pm4py
import logging

from pm4py.ocel import OCEL as Pm4pyEventLogObject
from model.ocel.base import OCEL
from pathlib import Path
import pandas as pd

logger = logging.getLogger("app_logger")


class Pm4pyEventLog(OCEL):
    """
    Event log wrapper using the pm4py module
    """

    def __init__(self, **kwargs):
        super().__init__(ocel_type="pm4py", **kwargs)

        if "ocel" in kwargs and isinstance(kwargs["ocel"], Pm4pyEventLogObject):
            self.ocel = kwargs["ocel"]
        elif "dataset" in kwargs:
            filename = str(Path("../data/datasets") / kwargs["dataset"])
            logger.info(f"Importing dataset {filename}")

            # https://pm4py.fit.fraunhofer.de/documentation#object-centric-event-logs
            self.ocel = pm4py.read_ocel(filename)
        else:
            raise ValueError("pm4py event log could not be instantiated.")

    def _get_object_types(self):
        return pm4py.ocel.ocel_get_object_types(self.ocel)

    def _get_object_type_counts(self):
        ot = self.ocel.objects['ocel:type']
        return ot.value_counts().to_dict()

    def _get_activities(self):
        ot_activity_dict = pm4py.ocel.ocel_object_type_activities(self.ocel)
        activities = set()
        for ot in ot_activity_dict:
            for activity in ot_activity_dict[ot]:
                activities.add(activity)
        return activities

    def _get_ot_activities(self):
        return pm4py.ocel.ocel_object_type_activities(self.ocel)

    def _compute_opera(self):
        return None  # Not supported, use ocpa

    def _get_cases(self):
        return None  # Not supported, use ocpa

    def _get_variants(self):
        return None  # Not supported, use ocpa

    def _get_variant_frequencies(self):
        return None  # Not supported, use ocpa

    def _get_variant_graph(self, variant_id):
        return None  # Not supported, use ocpa

    def _compute_petri_net(self):
        logger.info("Beggining the discovery of a petri net using pm4py")
        ocpn = pm4py.discover_oc_petri_net(self.ocel)
        filename = 'static/img/ocpn.png'
        pm4py.save_vis_ocpn(ocpn, filename)
        logger.info(f"Petri net saved to {filename}")
        return filename
    
    def _compute_heatmap(self, dpi=150) -> pd.DataFrame:
        df = self.ocel.relations
        collect = pd.DataFrame([],index=[],columns=['Events'])

        for x in set(df.loc[:,'ocel:type']):
            tmp = df.loc[lambda df: df['ocel:type'] == x]
            # print(tmp.loc[:,'ocel:eid'].tolist())
            tmp_list = tmp.loc[:,'ocel:eid'].tolist()
            tmp_df = pd.DataFrame([[tmp_list]], index=[x], columns=['Events'])
            collect = pd.concat([collect,tmp_df])

        matrix = pd.DataFrame([],index=[collect.index],columns=[collect.index])
        event_lists = collect.loc[:,'Events'].tolist()

        for x in range(len(event_lists)):
            for y in range(x,len(event_lists)):
                if x == y:
                    events = list(dict.fromkeys(event_lists[x]))
                    matrix.iloc[x,x]=events
                else:
                    events = [value for value in event_lists[x] if value in event_lists[y]]
                    matrix.iloc[x,y]=events
                    matrix.iloc[y,x]=events

        number_matrix = matrix.applymap(len)
        number_matrix = number_matrix.sort_index(axis=1)
        number_matrix = number_matrix.sort_index()
        return number_matrix

    def __hash__(self):
        # TODO test/fix this
        hash_df = lambda df: pd.util.hash_array(pd.util.hash_pandas_object(df).to_numpy())
        return [hash_df(self.ocel.events), hash_df(self.ocel.relations), hash_df(self.ocel.objects)]

    def export_json_ocel(self, target_path):
        pm4py.objects.ocel.exporter.jsonocel.exporter.apply(self.ocel, target_path)
