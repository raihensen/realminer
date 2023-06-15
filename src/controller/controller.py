
import logging
from view.view import View
from typing import Dict
from controller.tasks import *

logger = logging.getLogger("app_logger")


class Controller:
    view: View
    tasks: Dict[str, Task]
    TASKS: Dict

    def __init__(self, model):
        self.model = model
        self.tasks = {}
        self.TASKS = {}
        init_tasks(self)

    def init_view(self):
        self.view.init_object_types(object_types=self.model.ocel.object_types,
                                    counts=self.model.ocel.object_type_counts,
                                    colors=None,
                                    model=self.model)
        self.view.init_activities(activities=self.model.ocel.activities,
                                  model=self.model)

    def run_task(self, key: str, kill_if_running: bool = True, **kwargs):
        if key not in self.TASKS:
            logger.error(f"Controller: Task '{key}' not found.")
        task_args = self.TASKS[key]

        if key in self.tasks:
            if self.tasks[key].running and kill_if_running:
                self.tasks[key].kill()

        self.tasks[key] = Task(key, **task_args, **kwargs)
        self.tasks[key].start()

    def test_action(self):
        self.view.test_set_label(self.model.ocel.object_types)

