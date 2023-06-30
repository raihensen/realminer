import logging
from abc import ABC, abstractmethod
from typing import final
from builtins import property
from pprint import pprint
from pathlib import Path
# import pandas as pd
from typing import List, Dict, Union, Optional
import pandas as pd

import networkx as nx

logger = logging.getLogger("app_logger")


class OCEL(ABC):
    """
    Abstract event log wrapper class, to be extended by a library for object-centric event log management
    Offering a basic interface to access information or statistics on the event log
    """

    active_ot = None

    @abstractmethod
    def __init__(self, model, **kwargs):
        self.model = model
        if "ocel" not in kwargs:
            logger.info(f"OCEL instantiation with params {kwargs}")

    @abstractmethod
    def _get_object_types(self) -> List[str]:
        """ Returns the list of object types within the event log """

    @abstractmethod
    def _get_object_type_counts(self) -> Dict[str, int]:
        """ Returns the object counts wrt. the object type """

    @abstractmethod
    def _get_activities(self) -> List[str]:
        """ Returns the list of activity names within the event log """

    @abstractmethod
    def _get_ot_activities(self) -> Dict[str, List[str]]:
        """ Returns a dict mapping each object type to the list of activities they appear in """

    @abstractmethod
    def _compute_opera(self, agg: Union[List[str], str, None] = None) -> Optional[Dict[str, Dict[str, pd.DataFrame]]]:
        """ Computes object-centric KPIs as defined in the OPerA framework """

    @abstractmethod
    def _get_cases(self) -> List[str]:
        """ Returns the list of cases """

    @abstractmethod
    def _get_variants(self) -> List[str]:
        """ Returns the list of case variants (identified by a uid) """

    @abstractmethod
    def _get_variant_frequencies(self) -> Dict[str, int]:
        """ Returns the variant frequencies """

    @abstractmethod
    def _get_variant_graph(self, variant_id) -> nx.DiGraph:
        """ Returns the event-object graph of a given variant """

    @abstractmethod
    def _compute_petri_net(self):
        """Discovers an object-centric Petri net from the provided object-centric event log"""

    @abstractmethod
    def _compute_heatmap(self):
        """Computes a HeatMap of Object Relations from the provided object-centric event log"""

    @abstractmethod
    def _get_extended_table(self):
        """Returns the event log as a pandas DataFrame"""

    @property
    @final
    def object_types(self) -> List[str]:
        return self._get_object_types()

    @property
    @final
    def object_type_counts(self) -> List[str]:
        return self._get_object_type_counts()

    @property
    @final
    def activities(self) -> List[str]:
        return self._get_activities()

    @property
    @final
    def ot_activities(self) -> List[str]:
        return self._get_ot_activities()


class DummyEventLog(OCEL):
    """
    Dummy class with static responses, used for faster UI development
    """

    def __init__(self, model, **kwargs):
        super().__init__(model, ocel_type="dummy", **kwargs)

    def _get_object_types(self):
        return ["order", "item", "package", "delivery", "invoice"]

    def _get_object_type_counts(self):
        return {"order": 100, "item": 176, "package": 124, "delivery": 98, "invoice": 105}

    def _get_activities(self):
        return ["Place Order", "Pack Items", "Send Invoice", "Start Delivery", "Receive Payment", "Request Refund"]

    def _get_ot_activities(self):
        return []

    def _compute_opera(self):
        return {}

    def _get_extended_table(self):
        return None

    def _get_cases(self):
        freqs = [30, 18, 8, 7, 1, 1, 1]
        return list(zip(range(sum(freqs)), sum((x * [i] for i, x in enumerate(sorted(freqs, reverse=True))), [])))

    def _get_variants(self) -> Dict[int, int]:
        # TODO decide how to represent a variant
        return {i: i for i in range(7)}

    def _get_variant_frequencies(self) -> Dict[str, int]:
        return {}

    def _get_variant_graph(self, variant_id) -> nx.DiGraph:
        return None

    def _compute_petri_net(self):
        return None

    def _compute_heatmap(self):
        return None
