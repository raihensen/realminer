import logging
import os

from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

from model.ocel.base import OCEL, DummyEventLog
from model.ocel.ocpa import OcpaEventLog, OCPA_DEFAULT_SETTINGS
from model.ocel.pm4py import Pm4pyEventLog
from model.constants import *

backends = {
    BACKEND_OCPA: OcpaEventLog,
    BACKEND_PM4PY: Pm4pyEventLog,
    BACKEND_DUMMY: DummyEventLog
}

logger = logging.getLogger("app_logger")

class Model:
    ocel: OCEL

    def __init__(self, dataset):
        self.dataset = dataset

    def init_ocel(self, dataset, backend=BACKEND_PM4PY):
        event_log_constructor = backends[backend]
        self.ocel = event_log_constructor(**dataset)
        logger.info("OCEL loaded successfully")

    def update_active_ot_in_model(self, active_ot):
        self.ocel.active_ot = active_ot
        self.ocel.filter_ocel_by_active_ot()

    def get_opca_ocel(self):
        target_path = 'tmp.jsonocel'
        self.ocel.export_json_ocel(target_path)
        kwargs = self.dataset
        params = {k: kwargs.get(k, default) for k, default in OCPA_DEFAULT_SETTINGS.items()}
        logger.info("reading the filtered ocel for ocpa module")
        ocpa_ocel = ocel_import_factory.apply(target_path, parameters=params)
        os.remove(target_path)
        return ocpa_ocel
        

