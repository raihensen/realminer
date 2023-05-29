
from abc import ABC, abstractmethod
from typing import final
from builtins import property
from pprint import pprint
from pathlib import Path
# import pandas as pd
from typing import List


class OCEL(ABC):
    """
    Abstract event log wrapper class, to be extended by a library for object-centric event log management
    Offering a basic interface to access information or statistics on the event log
    """

    object_type_cache: list = None
    activity_cache: list = None

    @abstractmethod
    def __init__(self, **kwargs):
        print(f"OCEL instantiation with params {kwargs}")

    @abstractmethod
    def _get_object_types(self) -> List[str]:
        """ Returns the list of object types within the event log """

    @abstractmethod
    def _get_activities(self) -> List[str]:
        """ Returns the list of activity names within the event log """

    @property
    @final
    def object_types(self) -> List[str]:
        if self.object_type_cache is None:
            self.object_type_cache = self._get_object_types()
        return self.object_type_cache

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
        self.object_type_cache = None
        self.activity_cache = None


class DummyEventLog(OCEL):
    """
    Dummy class with static responses, used for faster UI development
    """
    def __init__(self, **kwargs):
        super().__init__(ocel_type="dummy", **kwargs)

    def _get_object_types(self):
        return ["order", "item", "package", "delivery", "invoice"]

    def _get_activities(self):
        return ["Place Order", "Pack Items", "Send Invoice", "Start Delivery", "Receive Payment", "Request Refund"]

