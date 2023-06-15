import logging

from view.view import View
from model.model import *
from model.constants import *
from controller.controller import *
import os

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

# instantiate logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)
# define handler and formatter
if not os.path.exists("../logs/"):
   os.makedirs("../logs")
file_handler = logging.FileHandler(r'../logs/app.log', mode='w')
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


class App:
    def __init__(self):
        dataset = DATASET_RECRUITING
        self.model = Model(dataset)
        self.model.init_ocel(dataset, backend=BACKEND_PM4PY)
        # self.model.init_ocel(dataset, backend=BACKEND_OCPA)

        self.controller = Controller(self.model)
        self.view = View(self.controller, theme="litera")
        self.controller.view = self.view

        self.controller.init_view()


if __name__ == "__main__":
    logger.info("Program started")
    app = App()
    app.view.start()
    logger.info("Program exited")
