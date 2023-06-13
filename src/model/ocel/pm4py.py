import pm4py
import logging

from ocpa.objects.log.ocel import OCEL as Pm4pyEventLogObject
from model.ocel.base import OCEL
from pathlib import Path

logger = logging.getLogger("app_logger")


class Pm4pyEventLog(OCEL):
    """
    Event log wrapper using the pm4py module
    """

    ocel: Pm4pyEventLogObject
    filtered_ocel: Pm4pyEventLogObject

    def __init__(self, dataset, **kwargs):
        super().__init__(ocel_type="pm4py", **kwargs)

        filename = str(Path("../data/datasets") / dataset)
        logger.info(f"Importing dataset {filename}")

        # https://pm4py.fit.fraunhofer.de/documentation#object-centric-event-logs
        self.ocel = pm4py.read_ocel(filename)
        self.filtered_ocel = self.ocel
        self.active_ot = pm4py.ocel.ocel_get_object_types(self.ocel)


    def _get_object_types(self):
        return pm4py.ocel.ocel_get_object_types(self.filtered_ocel)

    def _get_object_type_counts(self):
        ot = self.ocel.objects['ocel:type']
        return ot.value_counts().to_dict()

    def _get_activities(self):
        return pm4py.ocel.ocel_object_type_activities(self.filtered_ocel)

    def _get_cases(self):
        return []

    def _get_variants(self):
        return {}

    def _discover_petri_net(self):
        logger.info("Beggining the discovery of a petri net using pm4py")
        ocpn = pm4py.discover_oc_petri_net(self.filtered_ocel)
        filename = 'static/img/ocpn.png'
        pm4py.save_vis_ocpn(ocpn, filename)
        logger.info(f"Petri net saved to {filename}")
        return ocpn

    def filter_ocel_by_active_ot(self):
        # TODO: Once we add filtering by activities it will require an additional adjustment
        self.filtered_ocel = pm4py.filter_ocel_object_types(self.ocel, self.active_ot)

    def export_json_ocel(self, target_path):
        pm4py.objects.ocel.exporter.jsonocel.exporter.apply(self.filtered_ocel, target_path)
