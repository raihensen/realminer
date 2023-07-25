
import logging
from view.view import View
from typing import Dict, List, Union, Optional
from controller.tasks import *
from controller.export import Export

logger = logging.getLogger("app_logger")


class Controller:
    TASKS: Dict

    def __init__(self, model):
        self.model = model
        self.tasks = {}
        self.TASKS = {}
        init_tasks(self)
        self.current_exports = []  # Usually only the latest export (last element) is used

    def init_view(self):
        self.view.init_object_types(object_types=self.model.original_ocel.object_types,
                                    counts=self.model.original_ocel.object_type_counts,
                                    colors=None,
                                    model=self.model)
        self.view.init_activities(activities=self.model.original_ocel.activities,
                                  model=self.model)
        self.view.init_ocel_df(model=self.model)

    def pre_computations(self):
        """ Run as task: This function computes several statistics / visualizations on the model in the background,
        as soon as the window is ready. This way, the cached results are already available when requesting them later."""
        logger.info("Start pre-computations...")
        _ = self.model.compute_opera()
        # ...
        logger.info("Pre-computations finished.")

    def render_petri_net(self, renderer):
        # run as task
        # Call discovery (within Model)
        ocpn = self.model.compute_petri_net()
        # Call performance metrics (within Model)
        opera_kpis = self.model.compute_opera()
        # Call renderer (within View)
        path = renderer(ocpn, opera_kpis["lagging_time"], opera_kpis["pooling_time"])
        return path

    def compute_cases(self):
        # run as task
        return self.model.cases

    def compute_variants(self):
        # run as task
        return self.model.variants

    def compute_variant_frequencies(self):
        # run as task
        return self.model.variant_frequencies

    def compute_opera(self, agg: Union[List[str], str]):
        # run as task
        return self.model.compute_opera(agg)

    def run_task(self, key: str, kill_if_running: bool = True, **kwargs):
        if key not in self.TASKS:
            logger.error(f"Controller: Task '{key}' not found.")
            return
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

    def init_export(self, export: Export):
        """
        Adds an Export object to the list of available exports
        :param export:
        :return:
        """
        self.current_exports.append(export)

    def trigger_export(self, name: Optional[str] = None) -> bool:
        """
        Triggers the export function of the latest Export added to the list self.current_exports.
        :param name: Filter the export list for a certain name, take the latest matching Export instance.
        :return: The latest (matching) Export object
        """
        if not self.current_exports:
            logger.info("Nothing to be exported.")
            return False

        if name is not None:
            matching_exports = [e for e in self.current_exports if e.name == name]
            if not matching_exports:
                logger.info(f"No export available with the name '{name}'")
                return False
            export = matching_exports[-1]
        else:
            export = self.current_exports[-1]

        logger.info(f"Export '{export.name}' triggered")
        export.prepare_path()
        return export.execute()
