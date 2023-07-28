import logging
from pathlib import Path
from typing import Dict, List, Union, Optional

import numpy as np
import pandas as pd
from ocpa.algo.discovery.ocpn import algorithm as ocpn_discovery_factory
from ocpa.algo.enhancement.token_replay_based_performance import algorithm as performance_factory
from ocpa.algo.util.process_executions.factory import LEAD_TYPE
from ocpa.algo.util.variants.factory import TWO_PHASE
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory

from model.ocel.base import OCEL

OCPA_DEFAULT_SETTINGS = {
    "execution_extraction": LEAD_TYPE,
    "leading_type": None,
    "variant_calculation": TWO_PHASE,
    "exact_variant_calculation": False
}

OPERA_OT_MEASURES = ["lagging_time", "pooling_time"]
OPERA_OVERALL_MEASURES = ['waiting_time', 'service_time', 'sojourn_time', 'synchronization_time', 'flow_time']
OPERA_MEASURES = OPERA_OVERALL_MEASURES + OPERA_OT_MEASURES

logger = logging.getLogger("app_logger")

MULTILINE_GRAPH_LABELS = True


class OcpaEventLog(OCEL):
    """
    Event log wrapper using the ocpa module
    """

    def __init__(self, model, dataset, **kwargs):
        super().__init__(model, ocel_type="ocpa", **kwargs)

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
        return None  # Use pm4py

    def _compute_opera(self, agg: Union[List[str], str, None] = None) -> Optional[Dict[str, Dict[str, pd.DataFrame]]]:
        """
        Performs OPerA computations on the OCEL.
        Includes waiting, service, sojourn, synchronization, flow time (not object type-related)
        and lagging and pooling time (object type-related)
        Supports different aggregation functions.
        :param agg: A list containing one or more of 'mean', 'min', 'max', or a single one of these strings
        :return: A dict containing multiple pandas DataFrames with the requested KPIs.
        """
        opera_params = {
            'measures': ['act_freq', 'arc_freq', 'object_count', *OPERA_MEASURES],
            'agg': ['mean', 'min', 'max'],
            'format': 'png'}

        logger.info("Computing OPERA measures...")
        ocpn = ocpn_discovery_factory.apply(self.ocel, parameters={"debug": False})
        diag = performance_factory.apply(ocpn, self.ocel, parameters=opera_params)
        logger.info("Computing OPERA completed ")
        # gviz = ocpn_viz_factory.apply(ocpn, diagnostics=diag, variant="annotated_with_opera", parameters=opera_params)
        L_ACT = list(self.activities)
        L_MEA_OVR = OPERA_OVERALL_MEASURES
        L_MEA_OTS = OPERA_OT_MEASURES
        L_OTS = self.object_types
        L_AGG = ["mean", "min", "max"]

        L_LEVELS = ["activity", "measure", "agg"]
        L_LEVELS_OT = ["activity", "measure", "object_type", "agg"]
        # ocpn_viz_factory.view(gviz)

        # Select aggregation function
        # if agg is None:
        #     agg = ['mean']
        # aggs = [agg] if isinstance(agg, str) else agg
        # aggs = [L_AGG.index(a) for a in aggs if a in L_AGG]
        # if not aggs:
        #     aggs = [L_AGG.index('mean')]

        aggs = L_AGG
        aggs = [L_AGG.index(a) for a in aggs if a in L_AGG]

        # Related to ONE object type
        A_OTS = np.array([[[[diag[act][mea].get(ot, {}).get(agg, None)
                         for agg in L_AGG] for ot in L_OTS]
                       for mea in L_MEA_OTS] for act in L_ACT])

        # Not related to object types
        A_OVR = np.array([[[diag[act][mea][agg] for agg in L_AGG] for mea in L_MEA_OVR] for act in L_ACT])

        # Summarize everything in dict of DataFrames
        dfs = {**{mea: {L_AGG[agg]: pd.DataFrame(A_OTS[:, i, :, agg], columns=L_OTS, index=L_ACT) for agg in aggs}
                  for i, mea in enumerate(OPERA_OT_MEASURES)},
               **{mea: {L_AGG[agg]: pd.Series(A_OVR[:, i, agg], index=L_ACT) for agg in aggs}
                  for i, mea in enumerate(L_MEA_OVR)}}
        self.opera_diagnostic = dfs
        return dfs

    def _get_cases(self) -> Dict[int, str]:
        return self.ocel.process_executions

    def _get_variants(self) -> List[str]:
        return self.ocel.variants

    def _get_variant_frequencies(self) -> Dict[str, int]:
        return dict(zip(self.ocel.variants, self.ocel.variant_frequencies))

    def _get_variant_graph(self, variant_id):
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
        ot_label_connector = "\n" if MULTILINE_GRAPH_LABELS else ", "
        ot_counts = {}
        for (i, j), edge in G.edges.items():
            edge_ots = {ot for ot, _ in edge_objects[(i, j)]}
            edge_ot_counts = {ot: len([obj for ot1, obj in edge_objects[(i, j)] if ot1 == ot]) for ot in edge_ots}
            label_parts = [f"{count}x {ot}" if count > 1 else ot for ot, count in edge_ot_counts.items()]
            edge["label"] = ot_label_connector.join(label_parts)
            ot_counts[(i, j)] = edge_ot_counts

        return G, ot_counts

    def _compute_petri_net(self):
        return None  # Use pm4py

    def _compute_heatmap(self):
        return None  # Use pm4py

    def _get_extended_table(self):
        return None  # Use pm4py
