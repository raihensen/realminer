
from model.ocel.base import OCEL, DummyEventLog
from model.ocel.ocpa import OcpaEventLog
from model.constants import *

backends = {
    BACKEND_OCPA: OcpaEventLog,
    # BACKEND_PM4PY: Pm4pyEventLog,
    BACKEND_DUMMY: DummyEventLog
}


class Model:
    ocel: OCEL

    def __init__(self):
        pass

    def init_ocel(self, dataset, backend=BACKEND_OCPA):
        event_log_constructor = backends[backend]
        self.ocel = event_log_constructor(**dataset)
        print("OCEL loaded successfully")
