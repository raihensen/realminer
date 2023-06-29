import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkfontawesome import icon_to_image as fontawesome
from PIL import Image, ImageTk
import os
from pprint import pprint

import plotly.graph_objects as go

# from view.components.scrollable_frame import VerticalScrolledFrame
from view.constants import *
from view.components.accordion import Accordion
from view.widgets.object_types import ObjectTypeWidget
from view.widgets.activities import ActivityWidget
from view.widgets.table_view import TableViewWidget
from view.widgets.heatmap import HeatmapFrame, HeatmapType, HEATMAP_HTML_FILE
from view.components.tab import Tabs, Tab, SidebarTab
from view.components.zoomable_frame import AdvancedZoom
from controller.tasks import *

if os.getlogin() == "RH":
    MAXIMIZED = True
else:
    MAXIMIZED = False
SIDEBAR_WIDTH_RATIO = 0.2
SIDEBAR_MIN_WIDTH = 150
TOOLBAR_HEIGHT = 40

HEATMAP_TYPES = {
    "object_interactions": HeatmapType(title="Object Interactions",
                                       description="Lorem Ipsum", task=TASK_HEATMAP_OT,
                                       get_callback=lambda tab: tab.display_heatmap_ot),
    "performance_metrics": HeatmapType(title="Performance Metrics",
                                       description="Lorem Ipsum", task=TASK_HEATMAP_OT,
                                       get_callback=lambda tab: tab.display_heatmap_ot),
    "oc_performance_metrics": HeatmapType(title="Object-centric Performance Metrics",
                                          description="Lorem Ipsum", task=TASK_HEATMAP_OT,
                                          get_callback=lambda tab: tab.display_heatmap_ot)
}

logger = logging.getLogger("app_logger")


def view():
    return View.instance


class FilterTab(SidebarTab):
    def __init__(self, master):
        super().__init__(master=master,
                         title="Filters and Settings",
                         sidebar_width_ratio=SIDEBAR_WIDTH_RATIO,
                         sidebar_min_width=SIDEBAR_MIN_WIDTH)

        # Sidebar contents
        acc = Accordion(self.sidebar, title_height=50, bootstyle=SECONDARY)
        acc.pack(side=TOP, fill=X, expand=True)
        # Object types
        self.ot_container = acc.add_chord(title='Object types', expanded=True)
        self.ot_widget = None
        # Activities
        self.act_container = acc.add_chord(title='Activities')
        self.act_widget = None
        # Table
        self.table_widget = None
        self.refresh_table_button = None

    def on_open(self):
        if self.table_widget is not None:
            self.table_widget.update_table()

    def init_table(self, model):
        self.table_widget = TableViewWidget(self.interior, model)
        self.refresh_table_button = tk.Button(self.interior, text="Refresh Table",
                                              command=self.table_widget.update_table)
        self.refresh_table_button.pack(side=BOTTOM, padx=10, pady=10, fill=X)


class PetriNetTab(Tab):
    def __init__(self, master):
        super().__init__(master=master, title="Petri Net")
        self.display_label = ttk.Label(self)
        self.imgview = None

    def on_open(self):
        view().controller.run_task(key=TASK_DISCOVER_PETRI_NET, callback=self.display_petri_net)

    def display_petri_net(self, path):
        if self.imgview is not None:
            self.imgview.canvas.forget()
            self.imgview.forget()
        self.imgview = AdvancedZoom(self, path=path)
        self.imgview.pack(fill=BOTH, expand=True)


class HeatMapTab(SidebarTab):
    def __init__(self, master):
        super().__init__(master=master,
                         title="Heatmap",
                         sidebar_width_ratio=SIDEBAR_WIDTH_RATIO,
                         sidebar_min_width=SIDEBAR_MIN_WIDTH)
        self.display_label = ttk.Label(self.interior)
        self.imgview = None

        # Prepare heatmap types
        for heatmap_type in HEATMAP_TYPES.values():
            heatmap_type.controller = view().controller
            heatmap_type.callback = heatmap_type.get_callback(self)

        # Heatmap selection
        selection_info_label = tk.Message(self.sidebar,
                                          width=self.sidebar.winfo_width() - 20,
                                          text=f"Below, you can select between different types of heatmaps.")
        selection_info_label.pack(fill=X)
        self.heatmap_selection = ttk.Frame(master=self.sidebar)
        self.heatmap_selection.pack(fill=BOTH)
        self.heatmap_selection_var = tk.IntVar()
        self.heatmap_selection_var.set(0)
        for i, (key, heatmap_type) in enumerate(HEATMAP_TYPES.items()):
            heatmap_type_row = ttk.Frame(master=self.heatmap_selection)
            heatmap_type_row.pack(fill=X, padx=5, pady=2)
            radio = ttk.Radiobutton(master=heatmap_type_row,
                                    value=i,
                                    variable=self.heatmap_selection_var,
                                    text=heatmap_type.title,
                                    command=self.generate_heatmap)
            radio.pack(side=LEFT, fill=X)

        # Init heatmap frame with default heatmap (object interactions)
        key, heatmap_type = self.get_selected_heatmap_type()
        self.frame = HeatmapFrame(self.interior, key=key, heatmap_type=heatmap_type)
        self.frame.pack(fill=BOTH, expand=YES)

    def on_open(self):
        # Compute OPerA KPIs. Argument `agg` can be changed to any of 'min', 'max' or 'mean'.
        # view().controller.run_task(key=TASK_OPERA, callback=self.display_opera, agg='mean')
        # Compute selected heatmap
        self.generate_heatmap()
        # view().controller.run_task(key=TASK_HEATMAP_OT, callback=self.display_heatmap_ot)

    def display_opera(self, kpis):
        pprint(kpis)

    def get_selected_heatmap_type(self):
        return list(HEATMAP_TYPES.items())[self.heatmap_selection_var.get()]

    def generate_heatmap(self):
        key, heatmap_type = self.get_selected_heatmap_type()
        print(f"Compute heatmap '{heatmap_type.title}'")
        heatmap_type.generate()
        # The above call schedules a task, with a callback that then displays the heatmap.

    def display_heatmap_ot(self, number_matrix):
        fig = go.Figure()
        fig.add_trace(go.Heatmap(z=number_matrix,
                                 x=list(number_matrix.columns.levels[0]),
                                 y=list(number_matrix.columns.levels[0])))
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()

    def refresh_heatmap_display(self):
        browser = self.frame.get_browser()
        if browser is not None:
            browser.Reload()
        else:
            print("Could not reload to show heatmap, browser is None")


class VariantsTab(SidebarTab):
    def __init__(self, master):
        super().__init__(master=master,
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
        view().controller.run_task(TASK_COMPUTE_VARIANT_FREQUENCIES, callback=self.display_variants)

    def display_variants(self, variant_frequencies):
        variant_frequencies = dict(sorted(variant_frequencies.items(), key=lambda item: item[1], reverse=True))
        labels = [f"Variant #{i} with frequency: {freq:.4f}" for i, freq in enumerate(variant_frequencies.values())]
        self.label_to_variant = dict(zip(labels, variant_frequencies.keys()))
        self.value_to_variant = dict(enumerate(variant_frequencies.keys()))

        num_proc, num_var = len(view().controller.model.cases), len(variant_frequencies)

        self.stats_label = tk.Message(self.sidebar,
                                      width=self.sidebar.winfo_width() - 20,
                                      text=f"There are {num_proc} process executions of {num_var} variants. In the list below, these variants are listed by their frequency (descending).")
        self.stats_label.pack(fill=X)

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

    def display_selected_variant(self):
        variant_id = self.value_to_variant[self.variant_selection_var.get()]
        path = view().controller.model.variant_graph(variant_id)

        if self.imgview is not None:
            self.imgview.canvas.forget()
            self.imgview.forget()
        self.imgview = AdvancedZoom(self.main, path=path)
        self.imgview.pack(fill=BOTH, expand=True)


class View:
    instance = None

    def __init__(self, controller, window: tk.Tk, theme):
        View.instance = self
        self.controller = controller

        # Recycle the welcome screen's window (only one Tk instance per run)
        self.window = window
        for w in self.window.winfo_children():
            w.destroy()
        self.window.title(WINDOW_TITLE)
        if MAXIMIZED:
            self.window.state('zoomed')
        self.window.resizable(width=True, height=True)

        self.theme = theme

        # Basic layout
        style = ttk.Style(theme)
        self.toolbar = ttk.Frame(master=self.window, bootstyle=DARK)
        # self.toolbar.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        self.toolbar.pack(side=TOP, fill=X)

        # Tabs
        self.tab_widget = Tabs(master=self.window)
        self.tab_widget.pack(side=TOP, fill=BOTH, expand=True)

        # create a new frame
        self.tab1 = FilterTab(self.tab_widget)
        self.tab_widget.add_tab(self.tab1)
        self.tab2 = PetriNetTab(self.tab_widget)
        self.tab_widget.add_tab(self.tab2)
        self.tab3 = HeatMapTab(self.tab_widget)
        self.tab_widget.add_tab(self.tab3)
        self.tab4 = VariantsTab(self.tab_widget)
        self.tab_widget.add_tab(self.tab4)

        # Toolbar contents
        ttk.Label(master=self.toolbar, text="[Toolbar]", bootstyle=DARK).pack(side=LEFT)

        # Theme selection
        theme_menubutton = ttk.Menubutton(master=self.toolbar, text="Change theme", bootstyle=DARK)
        theme_menubutton.pack(side=RIGHT, padx=10, pady=10, fill=Y)
        theme_menu = ttk.Menu(theme_menubutton)
        theme_var = tk.StringVar(value=self.theme)
        for theme in ttk.style.STANDARD_THEMES:
            theme_menu.add_radiobutton(label=theme,
                                       variable=theme_var,
                                       command=lambda t=theme: self.change_theme(t))
        theme_menubutton["menu"] = theme_menu

    def init_object_types(self, object_types, counts, model, colors=None):
        self.tab1.ot_widget = ObjectTypeWidget(self.tab1.ot_container, object_types, counts, model, colors)
        self.tab1.ot_widget.pack(fill=X)

    def init_activities(self, activities, model):
        self.tab1.act_widget = ActivityWidget(self.tab1.act_container, activities, model)
        self.tab1.act_widget.pack(fill=X)

    def init_ocel_df(self, model):
        self.tab1.init_table(model)

    def change_theme(self, theme):
        logger.info(f"Change to theme '{theme}'")
        self.style.theme_use(theme)

    @property
    def style(self):
        return ttk.style.Style.instance
