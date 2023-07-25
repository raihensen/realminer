
import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from view.constants import *
from view.components.tab import Tabs, Tab, SidebarTab
from controller.tasks import *
from controller.export import Export
from view.components.zoomable_frame import AdvancedZoom
from view import utils
import pm4py
import time
import pm4py.visualization.ocel.ocpn.visualizer as petrinet_visualizer
from pm4py.visualization.ocel.ocpn.variants.wo_decoration import *
# import uuid
from typing import Optional, Dict, Any, Tuple
import pandas as pd


class PetriNetTab(Tab):
    def __init__(self, master, view):
        super().__init__(master=master, view=view, title="Petri Net")
        self.display_label = ttk.Label(self)
        self.imgview = None

    def on_open(self):
        self.view.controller.run_task(key=TASK_DISCOVER_PETRI_NET, callback=self.display_petri_net, renderer=self.render_petri_net)
        self.view.show_toast(title="Process model discovery", message=TAB_EXPLANATION_PETRI_NET, bootstyle='dark')

    def display_petri_net(self, path):
        if self.imgview is not None:
            self.imgview.canvas.forget()
            self.imgview.forget()
        self.imgview = AdvancedZoom(self, path=path)
        self.imgview.pack(fill=BOTH, expand=True)
        self.view.controller.init_export(Export("petrinet", "png", copy_from_path=path, use_dialog=True))

    def render_petri_net(self, ocpn, lagging_times: pd.DataFrame, pooling_times: pd.DataFrame):
        """
        Renders an object-centric petri net (ocpn) to an image file.
        Based on pm4py's visualization method (https://github.com/pm4py/pm4py-core/blob/release/pm4py/visualization/ocel/ocpn/variants/wo_decoration.py)
        Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.
        :param ocpn: An object-centric petri net, as discovered by pm4py's discovery algorithm
        :return: The path of the rendered image
        """
        # bgcolor = ttk.Style.instance.colors.bg

        t0 = time.time()
        # A = petrinet_visualizer.apply(ocpn)
        A, maps = self.advanced_visualizer(ocpn, lagging_times, pooling_times, agg='mean')
        t1 = time.time()
        visualization_time = t1 - t0

        A.graph_attr["fontname"] = GRAPH_FONT
        A.node_attr["fontname"] = GRAPH_FONT
        A.edge_attr["fontname"] = GRAPH_FONT
        A.graph_attr["bgcolor"] = ttk.Style.instance.colors.bg
        A.node_attr["color"] = ttk.Style.instance.colors.fg
        A.node_attr["fontcolor"] = ttk.Style.instance.colors.fg
        A.edge_attr["fontcolor"] = ttk.Style.instance.colors.fg
        A.graph_attr['dpi'] = str(GRAPHVIZ_RENDER_DPI)

        filename = 'tmp/ocpn.png'
        A.name = "ocpn"
        A.format = "png"
        t0 = time.time()
        path = A.render(format="png", outfile=filename).replace('\\', '/')
        t1 = time.time()
        render_time = t1 - t0
        logger.info(f"Petri net saved to {path}")
        logger.info(f"Visualization time: {visualization_time}")
        logger.info(f"Render time: {render_time}")
        return path

    def advanced_visualizer(self, ocpn: Dict[str, Any],
                            lagging_times: pd.DataFrame,
                            pooling_times: pd.DataFrame,
                            agg: str,
                            parameters: Optional[Dict[Any, Any]] = None) -> Tuple[Digraph, Dict[str, Any]]:
        """
        Obtains a visualization of the provided object-centric Petri net (without decoration).
        Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

        Parameters
        ----------------
        ocpn
            Object-centric Petri net
        lagging_times
        pooling_times
            DataFrame containing performance metrics computed with the OPerA framework
        agg
            One of 'min', 'mean' and 'max'. Aggregation used for performance metrics.
        parameters
            Variant-specific parameters:
            - Parameters.FORMAT => the format of the visualization ("png", "svg", ...)
            - Parameters.BGCOLOR => the background color
            - Parameters.RANKDIR => the rank direction (LR = left-right, TB = top-bottom)

        Returns
        ---------------
        viz
            Graphviz digraph
        """
        if parameters is None:
            parameters = {}

        image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
        bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)
        rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, "LR")

        filename = tempfile.NamedTemporaryFile(suffix='.gv')
        viz = Digraph("ocdfg", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
        viz.attr('node', shape='ellipse', fixedsize='false')

        activities_map = {}
        source_places = {}
        target_places = {}
        transition_map = {}
        places = {}

        for act in ocpn["activities"]:
            activities_map[act] = str(uuid.uuid4())
            viz.node(activities_map[act], label=act, shape="box")

        for ot in ocpn["object_types"]:
            otc = ot_to_color(ot)
            source_places[ot] = str(uuid.uuid4())
            target_places[ot] = str(uuid.uuid4())
            viz.node(source_places[ot], label=ot, shape="ellipse", style="filled", fillcolor=otc)
            viz.node(target_places[ot], label=ot, shape="underline", fontcolor=otc)

        for ot in ocpn["petri_nets"]:
            otc = ot_to_color(ot)
            net, im, fm = ocpn["petri_nets"][ot]
            for place in net.places:
                if place in im:
                    places[place] = source_places[ot]
                elif place in fm:
                    places[place] = target_places[ot]
                else:
                    places[place] = str(uuid.uuid4())
                    viz.node(places[place], label=" ", shape="circle", style="filled", fillcolor=otc)
            for trans in net.transitions:
                if trans.label is not None:
                    transition_map[trans] = activities_map[trans.label]
                else:
                    transition_map[trans] = str(uuid.uuid4())
                    viz.node(transition_map[trans], label=" ", shape="box", style="filled", fillcolor=otc)

            for arc in net.arcs:
                if type(arc.source) is PetriNet.Place:
                    is_double = arc.target.label in ocpn["double_arcs_on_activity"][ot] and ocpn["double_arcs_on_activity"][ot][arc.target.label]
                    penwidth = "4.0" if is_double else "1.0"
                    label = None
                    viz.edge(places[arc.source], transition_map[arc.target], color=otc, penwidth=penwidth, label=label)
                elif type(arc.source) is PetriNet.Transition:
                    is_double = arc.source.label in ocpn["double_arcs_on_activity"][ot] and ocpn["double_arcs_on_activity"][ot][arc.source.label]
                    penwidth = "4.0" if is_double else "1.0"


                    act = arc.source.label
                    lagging_time = lagging_times[agg][ot].get(act, None)
                    pooling_time = pooling_times[agg][ot].get(act, None)
                    label = "\n".join([f"Lagging: {utils.time_formatter(lagging_time)}"] if lagging_time else [] +
                                      [f"Pooling: {utils.time_formatter(pooling_time)}"] if pooling_time else [])

                    viz.edge(transition_map[arc.source], places[arc.target], color=otc, penwidth=penwidth, label=label)

        viz.attr(rankdir=rankdir)
        viz.format = image_format

        maps = {
            "activities": activities_map,
            "source_places": source_places,
            "target_places": target_places,
            "transitions": transition_map,
            "places": places,
        }
        return viz, maps
