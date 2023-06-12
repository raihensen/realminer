import logging

from model.ocel.base import OCEL, DummyEventLog
from model.ocel.ocpa import OcpaEventLog
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

    def __init__(self):
        pass

    def init_ocel(self, dataset, backend=BACKEND_PM4PY):
        event_log_constructor = backends[backend]
        self.ocel = event_log_constructor(**dataset)
        logger.info("OCEL loaded successfully")
