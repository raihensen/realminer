
from threading import Thread
import logging

logger = logging.getLogger("app_logger")

TASK_DISCOVER_PETRI_NET = "discover_petri_net"


def init_tasks(controller):
    controller.TASKS = {
        TASK_DISCOVER_PETRI_NET: {"func": controller.model.ocel.discover_petri_net}
    }


class Task(Thread):
    instance_counter = 0

    def __init__(self, key, func, callback, **kwargs):
        super().__init__()
        Task.instance_counter += 1
        self.id = f"{Task.instance_counter}_{key}"
        self.key = key
        self.func = func
        self.params = kwargs
        self.callback = callback
        self.running = False
        self.killed = False

    def run(self, **kwargs):
        self.running = True
        logger.info(f"Run task '{self.id}'")
        # Execute task
        response = self.func(**self.params, **kwargs)
        # Task finished
        self.running = False
        logger.info(f"Task '{self.id}' finished")
        if not self.killed:
            if self.callback is not None and callable(self.callback):
                if response is not None:
                    self.callback(response)
                else:
                    self.callback()

    def kill(self):
        self.killed = True
        logger.info(f"Task '{self.id}' killed")

