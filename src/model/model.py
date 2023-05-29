
from src.model.ocel.base import OCEL, DummyEventLog
# from src.model.ocel.ocpa import OcpaEventLog


class Model:
    ocel: OCEL

    def __init__(self):
        pass

    def init_ocel(self, dataset):
        # self.ocel = OcpaEventLog(**dataset)
        self.ocel = DummyEventLog()
        print("OCEL loaded successfully")
