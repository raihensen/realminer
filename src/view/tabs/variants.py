
import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from view.constants import *
from view.components.tab import Tabs, Tab, SidebarTab
from controller.tasks import *
from controller.export import Export
from view.components.zoomable_frame import AdvancedZoom
from networkx.drawing.nx_agraph import to_agraph


class VariantsTab(SidebarTab):
    def __init__(self, master, view):
        super().__init__(master=master,
                         view=view,
                         title="Variants Explorer",
                         sidebar_width_ratio=SIDEBAR_WIDTH_RATIO,
                         sidebar_min_width=120)
        self.stats_label = None
        self.variant_selection = None
        self.imgview = None
        self.label_to_variant = {}
        self.value_to_variant = {}
        self.variant_selection_var = tk.IntVar()

    def on_open(self):
        for w in [self.stats_label, self.variant_selection, self.imgview]:
            if w is not None:
                w.forget()

        # Check if computing variants makes sense (https://ilya-fradlin.atlassian.net/browse/CO-28)
        # TODO

        # Compute variants in separate thread
        self.view.controller.run_task(TASK_COMPUTE_VARIANT_FREQUENCIES, callback=self.display_variants)
        self.view.show_toast(title="Explore Process Executions and Variants", message=TAB_EXPLANATION_VARIANTS, bootstyle='dark')

    def display_variants(self, variant_frequencies):
        variant_frequencies = dict(sorted(variant_frequencies.items(), key=lambda item: item[1], reverse=True))
        labels = [f"Variant #{i} with frequency: {freq:.4f}" for i, freq in enumerate(variant_frequencies.values())]
        self.label_to_variant = dict(zip(labels, variant_frequencies.keys()))
        self.value_to_variant = dict(enumerate(variant_frequencies.keys()))

        num_proc, num_var = len(self.view.controller.model.cases), len(variant_frequencies)

        self.stats_label = ttk.Label(self.sidebar,
                                     anchor=W,
                                     wraplength=self.sidebar.winfo_width() - 20,
                                     text=f"There are {num_proc} process executions of {num_var} variants. In the list below, these variants are listed by their frequency (descending).")
        self.stats_label.pack(fill=X)
        self.stats_label.bind('<Configure>',
                              lambda e: self.stats_label.config(wraplength=self.sidebar.winfo_width() - 20))

        max_freq = max(variant_frequencies.values())

        self.variant_selection = ttk.Frame(master=self.sidebar)
        self.variant_selection.pack(fill=BOTH)
        self.variant_selection_var.set(0)
        for i, freq in enumerate(variant_frequencies.values()):
            variant_row = ttk.Frame(master=self.variant_selection)
            variant_row.pack(fill=X, padx=5, pady=2)
            radio = ttk.Radiobutton(master=variant_row,
                                    value=i,
                                    variable=self.variant_selection_var,
                                    text=f"Variant #{i} ({freq:.1%})",
                                    command=self.display_selected_variant)
            radio.pack(side=LEFT, fill=X)

            freq_var = tk.IntVar()
            freq_var.set(int(freq / max_freq * 100))
            progressbar = ttk.Progressbar(master=variant_row, length=100, variable=freq_var)
            progressbar.pack(side=RIGHT, padx=15)

        self.display_selected_variant()

    def render_variant_graph(self, variant_id) -> str:
        """ Renders a variant graph, saving it to an image file. """
        G, ot_counts = self.view.controller.model.variant_graph(variant_id)

        bg = ttk.Style.instance.colors.bg
        fg = ttk.Style.instance.colors.fg
        A = to_agraph(G)
        A.graph_attr["fontname"] = GRAPH_FONT
        A.node_attr["fontname"] = GRAPH_FONT
        A.edge_attr["fontname"] = GRAPH_FONT
        A.graph_attr["bgcolor"] = bg
        A.node_attr["fontcolor"] = fg
        A.node_attr["color"] = fg
        A.node_attr["fillcolor"] = bg
        A.edge_attr["fontcolor"] = fg
        A.edge_attr["color"] = fg
        A.graph_attr["rankdir"] = "TB"  # would prefer LR, but edge labels might be long
        A.node_attr["shape"] = "box"
        A.layout('dot')
        A.graph_attr['dpi'] = GRAPHVIZ_RENDER_DPI
        path = f"tmp/variant_graph_{variant_id}.png"
        A.draw(path)
        return path

    def display_selected_variant(self):
        variant_id = self.value_to_variant[self.variant_selection_var.get()]
        path = self.render_variant_graph(variant_id)
        self.view.controller.current_export = Export("varient_graph", "png", copy_from_path=path, use_dialog=True)
        # path = self.view.controller.model.variant_graph(variant_id)

        if self.imgview is not None:
            self.imgview.canvas.forget()
            self.imgview.forget()
        self.imgview = AdvancedZoom(self.main, path=path)
        self.imgview.pack(fill=BOTH, expand=True)
