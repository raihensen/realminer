
from abc import ABC, abstractmethod
from builtins import property
from pprint import pprint
from pathlib import Path
# import pandas as pd
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP, LEAD_TYPE
from ocpa.algo.util.variants.factory import ONE_PHASE, TWO_PHASE
from ocpa.objects.log.ocel import OCEL as OCPA_OCEL


OCPA_DEFAULT_SETTINGS = {
    "execution_extraction": LEAD_TYPE,
    "leading_type": None,
    "variant_calculation": TWO_PHASE,
    "exact_variant_calculation": False
}


class OCEL(ABC):

    @abstractmethod
    def __init__(self, **kwargs):
        print(f"OCEL instantiation with params {kwargs}")

    @abstractmethod
    def get_object_types(self):
        print("get OTs")
        pass

    @property
    def object_types(self):
        return self.get_object_types()


class LocalOCEL(OCEL):
    ocel: OCPA_OCEL

    def __init__(self, dataset, **kwargs):
        super().__init__(ocel_type="ocpa", **kwargs)

        filename = Path("../data/datasets") / dataset
        print(f"Importing dataset {filename}")
        # https://ocpa.readthedocs.io/en/latest/eventlogmanagement.html
        params = {k: kwargs.get(k, default) for k, default in OCPA_DEFAULT_SETTINGS.items()}

        self.ocel = ocel_import_factory.apply(filename, parameters=params)

    def get_object_types(self):
        return self.ocel.object_types


