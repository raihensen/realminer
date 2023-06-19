import logging

from model.constants import *
from welcome_screen import WelcomeScreen
import os
from ocpa.algo.util.process_executions.factory import CONN_COMP, LEAD_TYPE
from ocpa.algo.util.variants.factory import ONE_PHASE, TWO_PHASE
import tkinter as tk
from view.constants import *

# Startup code of our app, initializing the main classes

# datasets from https://ocel-standard.org
DATASET_GITHUB = {"dataset": "github_pm4py.jsonocel", "leading_type": "case:concept:name"}
DATASET_O2C = {"dataset": "o2c.jsonocel", "leading_type": "BELNR"} # SAP
DATASET_P2P = {"dataset": "p2p.jsonocel", "leading_type": "BELNR"} # SAP
DATASET_TRANSFER = {"dataset": "transfer_order.jsonocel", "leading_type": "MATNR"} # SAP
DATASET_RECRUITING = {"dataset": "recruiting.jsonocel", "leading_type": "applications"}
DATASET_RECRUITING_500 = {"dataset": "recruiting_500.jsonocel", "leading_type": "applications"}
DATASET_RECRUITING_2000 = {"dataset": "recruiting_2000.jsonocel", "leading_type": "applications"}
DATASET_ORDER = {"dataset": "running-example.jsonocel", "leading_type": "xxx"}
DATASET_WINDOWS = {"dataset": "windows_events.jsonocel", "leading_type": "eventIdentifier"}
DATASET_TEST = {"dataset": "ocpa_test_data.jsonocel", "execution_extraction": CONN_COMP}

DATASET_OCPA_P2P = {"dataset": "p2p-normal.jsonocel", "execution_extraction": CONN_COMP}

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
        self.model = None
        self.view = None
        self.controller = None

        self.window = tk.Tk()

        # welcome screen
        welcome_screen = WelcomeScreen(self, self.window)
        welcome_screen.start()

    def initialize(self, file):
        logger.info("Initiating the app")

        from model.model import Model
        from controller.controller import Controller
        from view.view import View

        dataset = {
            "dataset": file,
            "execution_extraction": CONN_COMP
        }
        # dataset = DATASET_OCPA_P2P
        self.model = Model(dataset)
        self.model.init_ocel(dataset, backend=BACKEND_PM4PY)

        self.controller = Controller(self.model)
        self.view = View(self.controller, window=self.window, theme="litera")
        self.controller.view = self.view
        self.controller.init_view()

        self.view.start()

    def __del__(self):
        logging.info('Destructor called, app deleted.')


if __name__ == "__main__":
    logger.info("Program started")
    app = App()
    del app
    logger.info("Program exited")
