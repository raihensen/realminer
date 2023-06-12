import logging
from model.ocel.base import OCEL

from ocpa.objects.log.ocel import OCEL as OcpaEventLogObject
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP, LEAD_TYPE
from ocpa.algo.util.variants.factory import ONE_PHASE, TWO_PHASE

# import pandas as pd
from pathlib import Path
from pprint import pprint


OCPA_DEFAULT_SETTINGS = {
    "execution_extraction": LEAD_TYPE,
    "leading_type": None,
    "variant_calculation": TWO_PHASE,
    "exact_variant_calculation": False
}

logger = logging.getLogger("app_logger")

class OcpaEventLog(OCEL):
    """
    Event log wrapper using the ocpa module
    """

    ocel: OcpaEventLogObject

    def __init__(self, dataset, **kwargs):
        super().__init__(ocel_type="ocpa", **kwargs)

        filename = Path("../data/datasets") / dataset
        logger.info(f"Importing dataset {filename}")
        # https://ocpa.readthedocs.io/en/latest/eventlogmanagement.html
        params = {k: kwargs.get(k, default) for k, default in OCPA_DEFAULT_SETTINGS.items()}

        self.ocel = ocel_import_factory.apply(filename, parameters=params)

    def _get_object_types(self):
        return self.ocel.object_types

    def _get_object_type_counts(self):
        return {ot: len(self.ocel.obj.ot_objects(ot)) for ot in self.object_types}

    def _get_activities(self):
        return self.ocel.obj.activities

    def _get_cases(self):
        return []

    def _get_variants(self):
        return {}

