
import logging
from view.view import View
from typing import Dict
from controller.tasks import *

logger = logging.getLogger("app_logger")


class Controller:
    TASKS: Dict

    def __init__(self, model):
        self.model = model
        self.tasks = {}
        self.TASKS = {}
        init_tasks(self)

    def init_view(self):
        self.view.init_object_types(object_types=self.model.original_ocel.object_types,
                                    counts=self.model.original_ocel.object_type_counts,
                                    colors=None,
                                    model=self.model)
        self.view.init_activities(activities=self.model.original_ocel.activities,
                                  model=self.model)
        self.view.init_ocel_df(model=self.model)
        

    def compute_cases(self):
        # run as task
        return self.model.cases

    def compute_variants(self):
        # run as task
        return self.model.variants

    def compute_variant_frequencies(self):
        # run as task
        return self.model.variant_frequencies

    def run_task(self, key: str, kill_if_running: bool = True, **kwargs):
        if key not in self.TASKS:
            logger.error(f"Controller: Task '{key}' not found.")
        task_args = self.TASKS[key]

        if key in self.tasks:
            if self.tasks[key].running and kill_if_running:
                self.tasks[key].kill()

        self.tasks[key] = task = Task(self.view.window, key, **task_args, **kwargs)
        task.running = True

        # Init loop waiting for termination
        if task.has_callback():
            task.watch()

        # start task
        task.start()

    def test_action(self):
        self.view.test_set_label(self.model.object_types)

