
from view.view import View
from model.model import *
from model.constants import *
from controller.controller import *

# Startup code of our app, initializing the main classes

# datasets from https://ocel-standard.org
DATASET_GITHUB = {"dataset": "github_pm4py.jsonocel", "leading_type": "case:concept:name"}
DATASET_O2C = {"dataset": "o2c.jsonocel", "leading_type": "BELNR"} # SAP
DATASET_P2P = {"dataset": "p2p.jsonocel", "leading_type": "BELNR"} # SAP
DATASET_TRANSFER = {"dataset": "transfer_order.jsonocel", "leading_type": "MATNR"} # SAP
DATASET_RECRUITING = {"dataset": "recruiting.jsonocel", "leading_type": "applications"}
DATASET_ORDER = {"dataset": "running-example.jsonocel", "leading_type": "xxx"}
DATASET_WINDOWS = {"dataset": "windows_events.jsonocel", "leading_type": "eventIdentifier"}

# example dataset from celonis
DATASET_CELONIS = {"dataset": "celonis.jsonocel", "leading_type": "xxx"}


class App:
    def __init__(self):
        self.model = Model()
        self.controller = Controller(self.model)
        self.view = View(self.controller, theme="litera")
        self.controller.view = self.view

        dataset = DATASET_RECRUITING
        self.model.init_ocel(dataset, backend=BACKEND_OCPA)
        self.controller.init_view()


app = App()
app.view.start()
