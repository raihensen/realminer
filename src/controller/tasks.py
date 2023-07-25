
from threading import Thread
import logging

from view.widgets.spinner import Spinner

logger = logging.getLogger("app_logger")

CALLBACK_WATCH_DELAY = 100  # Loop duration [ms] when waiting for task termination, then invoking the callback

# ----- TASK DEFINITIONS -----------------------------------------------------------------------------------------------
TASK_PRE_COMPUTATIONS = "pre_computations"
TASK_DISCOVER_PETRI_NET = "discover_petri_net"
TASK_HEATMAP_OT = "heatmap_ot"
TASK_HEATMAP_POOLING = "heatmap_pooling"
TASK_HEATMAP_LAGGING = "heatmap_lagging"
TASK_COMPUTE_CASES = "cases"
TASK_COMPUTE_VARIANTS = "variants"
TASK_COMPUTE_VARIANT_FREQUENCIES = "variant_frequencies"
TASK_OPERA = "opera"


def init_tasks(controller):
    controller.TASKS = {
        TASK_PRE_COMPUTATIONS: {"func": controller.pre_computations},
        TASK_DISCOVER_PETRI_NET: {"func": controller.render_petri_net, "text": "Discovering petri net"},
        TASK_HEATMAP_OT: {"func": controller.model.compute_heatmap, "text": "Computing heatmap"},
        TASK_HEATMAP_POOLING: {"func": controller.model.compute_heatmap_pooling, "text": "Computing performance metrics"},
        TASK_HEATMAP_LAGGING: {"func": controller.model.compute_heatmap_lagging, "text": "Computing performance metrics"},
        TASK_COMPUTE_CASES: {"func": controller.compute_cases, "text": "Computing cases and variants"},
        TASK_COMPUTE_VARIANTS: {"func": controller.compute_variants, "text": "Computing cases and variants"},
        TASK_COMPUTE_VARIANT_FREQUENCIES: {"func": controller.compute_variant_frequencies, "text": "Computing variant frequencies"},
        TASK_OPERA: {"func": controller.compute_opera, "text": "Computing performance metrics"}
    }
# ----------------------------------------------------------------------------------------------------------------------


class Task(Thread):
    instance_counter = 0
    window = None

    def __init__(self, window, key, func, callback, text=None, **kwargs):
        super().__init__()
        Task.instance_counter += 1
        self.id = f"{Task.instance_counter}_{key}"
        self.window = window
        self.key = key
        self.func = func
        self.params = kwargs
        self.callback = callback
        self.text = text
        self.running = False
        self.response = None
        self.killed = False
        self.spinner = None

    def has_callback(self):
        return self.callback is not None and callable(self.callback)

    def run(self, **kwargs):
        self.running = True  # (might already have been set to true)
        logger.info(f"Run task '{self.id}'")

        # Show spinner
        self.show_spinner()

        # Execute task
        self.response = self.func(**self.params, **kwargs)
        # Task finished
        self.running = False
        logger.info(f"Task '{self.id}' finished")

        # Remove spinner
        self.spinner.stop()
        self.spinner.place_forget()
        self.spinner = None

    def show_spinner(self):
        # Creates a spinner inside the window with a description of the task
        if self.spinner is not None:
            self.spinner.set_text(self.text)
        else:
            self.spinner = Spinner(Task.window, text=f"{self.text} ...")
            self.spinner.overlay()

    def watch(self):
        """
        Loop waiting for the task to be finished, then executing the callback
        Necessary s.t. the callback is being called from the main thread
        """
        if self.killed:
            # callback will not be invoked
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

