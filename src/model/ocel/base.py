import logging
from abc import ABC, abstractmethod
from typing import final
from builtins import property
from pprint import pprint
from pathlib import Path
# import pandas as pd
from typing import List, Dict

logger = logging.getLogger("app_logger")

class OCEL(ABC):
    """
    Abstract event log wrapper class, to be extended by a library for object-centric event log management
    Offering a basic interface to access information or statistics on the event log
    """

    object_types_cache: list = None
    object_type_counts_cache: dict = None
    activity_cache: list = None
    case_cache: list = None
    variant_cache: dict = None
    ocpn_cache = None

    @abstractmethod
    def __init__(self, **kwargs):
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
    def _get_cases(self) -> List[str]:
        """ Returns the list of cases """

    @abstractmethod
    def _get_variants(self) -> List[str]:
        """ Returns the list of case variants """

    @abstractmethod
    def _discover_petri_net(self):
        """Discovers an object-centric Petri net from the provided object-centric event log"""

    @property
    @final
    def object_types(self) -> List[str]:
        if self.object_types_cache is None:
            self.object_types_cache = self._get_object_types()
        return self.object_types_cache

    @property
    @final
    def object_type_counts(self) -> List[str]:
        if self.object_type_counts_cache is None:
            self.object_type_counts_cache = self._get_object_type_counts()
        return self.object_type_counts_cache

    @property
    @final
    def activities(self) -> List[str]:
        if self.activity_cache is None:
            self.activity_cache = self._get_activities()
        return self.activity_cache

    @property
    @final
    def cases(self) -> List[str]:
        if self.case_cache is None:
            self.case_cache = self._get_cases()
        return self.case_cache

    @property
    @final
    def variants(self) -> List[str]:
        if self.variant_cache is None:
            self.variant_cache = self._get_variants()
        return self.variant_cache


    def discover_petri_net(self):
        if self.ocpn_cache is None:
            self.ocpn_cache = self._discover_petri_net()
        return self.ocpn_cache


    def reset_cache(self) -> None:
        """
        When any event log changes are made, this function is called.
        """
        self.object_types_cache = None
        self.object_type_counts_cache = None
        self.activity_cache = None
        self.case_cache = None
        self.variant_cache = None


class DummyEventLog(OCEL):
    """
    Dummy class with static responses, used for faster UI development
    """
    def __init__(self, **kwargs):
        super().__init__(ocel_type="dummy", **kwargs)

    def _get_object_types(self):
        return ["order", "item", "package", "delivery", "invoice"]

    def _get_object_type_counts(self):
        return {"order": 100, "item": 176, "package": 124, "delivery": 98, "invoice": 105}

    def _get_activities(self):
        return ["Place Order", "Pack Items", "Send Invoice", "Start Delivery", "Receive Payment", "Request Refund"]

    def _get_cases(self):
        freqs = [30, 18, 8, 7, 1, 1, 1]
        return list(zip(range(sum(freqs)), sum((x * [i] for i, x in enumerate(sorted(freqs, reverse=True))), [])))

    def _get_variants(self) -> Dict[int, int]:
        # TODO decide how to represent a variant
        return {i: i for i in range(7)}
