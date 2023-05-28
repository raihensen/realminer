
from src.model.ocel import OCEL, LocalOCEL
import random


class Model:
    ocel: OCEL

    def __init__(self):
        pass

    def init_ocel(self, dataset):
        self.ocel = LocalOCEL(**dataset)

    def random_number(self):
        return random.randint(1, 10)


