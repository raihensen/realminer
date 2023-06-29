import logging
from threading import Thread

from model.constants import *
from welcome_screen import WelcomeScreen
import os
import tkinter as tk
from tkinter import messagebox
from view.constants import *
from view.widgets.spinner import Spinner
from cefpython3 import cefpython as cef
import json

CONN_COMP = "connected_components"
LEAD_TYPE = "leading_type"

IMPORT_WATCH_DELAY = 100

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
        self.imports_finished = False
        self.model = None
        self.view = None
        self.controller = None
        self.load_preferences()

        # Start background imports
        self.import_thread = Thread(target=self.delayed_import)
        self.import_thread.start()

        self.window = tk.Tk()
        self.file = None

        # welcome screen
        welcome_screen = WelcomeScreen(self, self.window)

        self.window.mainloop()
        cef.Shutdown()

    def delayed_import(self):
        # Perform the delayed import inside a separate thread
        global Model, View, Controller
        from model.model import Model
        from controller.controller import Controller
        from view.view import View
        self.imports_finished = True

    def initialize(self, file):
        self.file = file
        if not self.imports_finished:
            logger.info("Waiting for background imports ...")
            # Spinner animation
            self._clear_window()
            Spinner(self.window).pack()
        self._initialize_after_imports()

    def _clear_window(self):
        for w in self.window.winfo_children():
            w.destroy()

    def _initialize_after_imports(self):
        global Model, View, Controller
        if not self.imports_finished:
            self.window.after(IMPORT_WATCH_DELAY, self._initialize_after_imports)
            return

        # Imports are finished
        logger.info("Imports done, initiating the app")

        dataset = {
            "dataset": self.file,
            "execution_extraction": CONN_COMP
        }
        # dataset = DATASET_OCPA_P2P
        self.model = Model(dataset)
        try:
            self.model.init_ocel(dataset, backend=BACKEND_PM4PY)
        except Exception:
            messagebox.showerror("Import failed", "The selected file could not be imported.")
            return

        self.controller = Controller(self.model)
        self.view = View(self, self.controller, window=self.window, theme="litera")
        self.controller.view = self.view
        self.controller.init_view()

    def load_preferences(self) -> dict:
        if os.path.exists(PREFERENCES_FILE):
            try:
                with open(PREFERENCES_FILE, 'r') as file:
                    contents = json.load(file)
            except json.JSONDecodeError:
                contents = {}
        else:
            contents = {}
        self.preferences = {
            "recent_files": [f for f in contents.get("recent_files", []) if os.path.exists(f)],
            "show_demo_popups": contents.get("show_demo_popups", True)
        }
        return self.preferences

    def set_preference(self, key: str, value):
        logger.info(f"Save new preference: {key} := {value}")
        self.preferences[key] = value
        with open(PREFERENCES_FILE, "w") as file:
            json.dump(self.preferences, file, indent=2)

    def __del__(self):
        logging.info('Destructor called, app deleted.')


if __name__ == "__main__":
    logger.info("Program started")
    app = App()
    del app
    logger.info("Program exited")
