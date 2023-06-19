import logging
from typing import Dict, List

from model.ocel.base import OCEL

from ocpa.objects.log.ocel import OCEL as OcpaEventLogObject
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP, LEAD_TYPE
from ocpa.algo.util.variants.factory import ONE_PHASE, TWO_PHASE

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph

# import pandas as pd
from pathlib import Path
from pprint import pprint

OCPA_DEFAULT_SETTINGS = {
    "execution_extraction": LEAD_TYPE,
    "leading_type": None,
    "variant_calculation": TWO_PHASE,
    "exact_variant_calculation": False
}

logger = logging.getLogger("app_logger")


class OcpaEventLog(OCEL):
    """
    Event log wrapper using the ocpa module
    """

    def __init__(self, dataset, **kwargs):
        super().__init__(ocel_type="ocpa", **kwargs)

        filename = Path("../data/datasets") / dataset
        logger.info(f"Importing dataset {filename}")
        # https://ocpa.readthedocs.io/en/latest/eventlogmanagement.html
        params = {k: kwargs.get(k, default) for k, default in OCPA_DEFAULT_SETTINGS.items()}

        self.ocel = ocel_import_factory.apply(filename, parameters=params)

    def _get_object_types(self):
        return self.ocel.object_types

    def _get_object_type_counts(self):
        return {ot: len(self.ocel.obj.ot_objects(ot)) for ot in self.object_types}

    def _get_activities(self):
        return self.ocel.obj.activities

    def _get_ot_activities(self):
        raise NotImplementedError()

    def _get_cases(self) -> Dict[int, str]:
        return self.ocel.process_executions  # TODO

    def _get_variants(self) -> List[str]:
        return self.ocel.variants

    def _get_variant_frequencies(self) -> Dict[str, int]:
        return dict(zip(self.ocel.variants, self.ocel.variant_frequencies))

    def _get_variant_graph(self, variant_id) -> str:
        """
        Computes a variant graph (event-object graph) and saves the output image to a file, returning the path.
        :param variant_id: The variant ID (hash)
        :return: The file path of the rendered image.
        """
        G, objects = self.ocel.variant_graphs[variant_id]

        # Retrieve object information to generate custom labels
        eids = list(G.nodes.keys())
        log = self.ocel.log.log
        variant_log = log[log.event_id.isin(eids)]
        event_objects = {eid: {(ot, oid) for ot, oid in objects if oid in variant_log.loc[eid, ot]} for eid in eids}
        edge_objects = {
            (i, j): event_objects[i] & event_objects[j] for i, j in G.edges
        }
        for i, node in G.nodes.items():
            node["label"] = log.loc[i, "event_activity"]
        for (i, j), edge in G.edges.items():
            edge_ots = {ot1 for ot1, _ in edge_objects[(i, j)]}
            edge_ot_counts = {ot: len([obj for ot1, obj in edge_objects[(i, j)] if ot1 == ot]) for ot in edge_ots}
            edge["label"] = ", ".join([f"{count}x {ot}" for ot, count in edge_ot_counts.items()])

        A = to_agraph(G)
        A.graph_attr["rankdir"] = "TB"
        A.layout('dot')
        path = f"tmp/variant_graph_{variant_id}.png"
        A.draw(path)
        return path

    def _compute_petri_net(self):
        return None  # Use pm4py

    def _compute_heatmap(self):
        return None  # Use pm4py
