
from abc import ABC, abstractmethod
from typing import final
from builtins import property
from pprint import pprint
from pathlib import Path
# import pandas as pd
from typing import List, Dict


class OCEL(ABC):
    """
    Abstract event log wrapper class, to be extended by a library for object-centric event log management
    Offering a basic interface to access information or statistics on the event log
    """

    object_types_cache: list = None
    object_type_counts_cache: dict = None
    activity_cache: list = None

    @abstractmethod
    def __init__(self, **kwargs):
        print(f"OCEL instantiation with params {kwargs}")

    @abstractmethod
    def _get_object_types(self) -> List[str]:
        """ Returns the list of object types within the event log """

    @abstractmethod
    def _get_object_type_counts(self) -> Dict[str, int]:
        """ Returns the object counts wrt. the object type """

    @abstractmethod
    def _get_activities(self) -> List[str]:
        """ Returns the list of activity names within the event log """

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
            self.activity_cache = self.get_activities()
        return self.activity_cache

    def reset_cache(self) -> None:
        """
        When any event log changes are made, this function is called.
        """
        self.object_types_cache = None
        self.object_type_counts_cache = None
        self.activity_cache = None


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

