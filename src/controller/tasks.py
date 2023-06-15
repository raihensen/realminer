
from threading import Thread
import logging

logger = logging.getLogger("app_logger")

CALLBACK_WATCH_DELAY = 100  # Loop duration [ms] when waiting for task termination, then invoking the callback

# ----- TASK DEFINITIONS -----------------------------------------------------------------------------------------------
TASK_DISCOVER_PETRI_NET = "discover_petri_net"
TASK_HEATMAP_OT = "heatmap_ot"


def init_tasks(controller):
    controller.TASKS = {
        TASK_DISCOVER_PETRI_NET: {"func": controller.model.ocel.discover_petri_net},
        TASK_HEATMAP_OT: {"func": controller.model.ocel.computeHeatMap}
    }
# ----------------------------------------------------------------------------------------------------------------------


class Task(Thread):
    instance_counter = 0

    def __init__(self, window, key, func, callback, **kwargs):
        super().__init__()
        Task.instance_counter += 1
        self.id = f"{Task.instance_counter}_{key}"
        self.window = window
        self.key = key
        self.func = func
        self.params = kwargs
        self.callback = callback
        self.running = False
        self.response = None
        self.killed = False

    def has_callback(self):
        return self.callback is not None and callable(self.callback)

    def run(self, **kwargs):
        self.running = True  # (might already have been set to true)
        logger.info(f"Run task '{self.id}'")

        # Execute task
        self.response = self.func(**self.params, **kwargs)
        # Task finished
        self.running = False
        logger.info(f"Task '{self.id}' finished")

    def watch(self):
        """
        Loop waiting for the task to be finished, then executing the callback
        Necessary s.t. the callback is being called from the main thread
        """
        if self.killed:
            # callback will not be invoked
            # TODO might include possibility to pass a second callback called when task is killed
            return
        elif not self.running:  # task has finished
            if self.has_callback():
                # just for safety reasons, if there is no callback, wait_for_termination should not be called in the first place.
                logger.info(f"Task '{self.id}': invoke callback")
                if self.response is not None:
                    self.callback(self.response)
                else:
                    self.callback()
        else:
            self.window.after(CALLBACK_WATCH_DELAY, self.watch)

    def kill(self):
        self.killed = True
        logger.info(f"Task '{self.id}' killed")

