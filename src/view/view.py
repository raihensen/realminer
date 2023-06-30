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
from view.utils import ResizeTracker
from view.components.accordion import Accordion
from view.widgets.object_types import ObjectTypeWidget
from view.widgets.activities import ActivityWidget
from view.widgets.table_view import TableViewWidget
from view.widgets.heatmap import HeatmapFrame, HeatmapType, HEATMAP_HTML_FILE
from view.components.tab import Tabs, Tab, SidebarTab
from view.components.zoomable_frame import AdvancedZoom
from controller.tasks import *
from view.widgets.popups import Toast

SIDEBAR_WIDTH_RATIO = 0.2
SIDEBAR_MIN_WIDTH = 150
TOOLBAR_HEIGHT = 40

HEATMAP_TYPES = {
    "object_interactions": HeatmapType(title="Object Interactions",
                                       description="Lorem Ipsum", task=TASK_HEATMAP_OT,
                                       get_callback=lambda tab: tab.display_heatmap_ot),
    "pooling_metrics": HeatmapType(title="Pooling Metrics",
                                   description="Lorem Ipsum", task=TASK_HEATMAP_POOLING,
                                   get_callback=lambda tab: tab.display_heatmap_pooling),
    "lagging_metrics": HeatmapType(title="Lagging Metrics",
                                   description="Lorem Ipsum", task=TASK_HEATMAP_LAGGING,
                                   get_callback=lambda tab: tab.display_heatmap_lagging)
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
        # Checkbox for disabling demo popups
        self.checkbox_demo_popups_var = tk.IntVar(value=int(view().app.get_preference("show_demo_popups")))
        self.checkbox_demo_popups = ttk.Checkbutton(master=self.sidebar,
                                                    text=f"Show instructions",
                                                    command=self.update_demo_popups_checkbox,
                                                    variable=self.checkbox_demo_popups_var,
                                                    bootstyle="round-toggle")
        self.checkbox_demo_popups.pack(side=BOTTOM, fill=X, padx=10, pady=10)
        # Theme selection
        theme_menubutton = ttk.Menubutton(master=self.sidebar, text="Change theme", bootstyle=SECONDARY)
        theme_menubutton.pack(side=BOTTOM, padx=10, pady=10, fill=X)
        theme_menu = ttk.Menu(theme_menubutton)
        theme_var = tk.StringVar(value=view().app.get_preference("theme"))
        for theme in ttk.style.STANDARD_THEMES:
            theme_menu.add_radiobutton(label=theme,
                                       variable=theme_var,
                                       command=lambda t=theme: view().change_theme(t))
        theme_menubutton["menu"] = theme_menu
        # Table
        self.table_widget = None
        self.refresh_table_button = None

    def update_demo_popups_checkbox(self):
        state = bool(self.checkbox_demo_popups_var.get())
        view().app.set_preference("show_demo_popups", state)

    def on_open(self):
        if self.table_widget is not None:
            self.table_widget.update_table()

        view().show_toast(
            title="Welcome to REAL MINER",
            message="By importing your event log, you have already done the first step. Let this notifications guide you through the discovery of your process. \n If you do not need any instruction, you can disable them in the welcome screen. \n You are currently in the filter and settings tab. In this tab, you can filter your event log by object types and activities. You can decide what is important for you. If you are not so sure about your log for now, you can also see it in this tab in the displayed table. For a more graphical overwiew you can open the Variants Tab next.",
            bootstyle="dark"
        )

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

        view().show_toast(
            title="Process model discovery",
            message="In this tab, you can see the process model for your process. It consists of all activities of your process and is able to replay every trace. With this, you should already have a good overview of your process. It is now time to dive deeper in the analysis of your process in the heatmap tab.",
            bootstyle='dark'
        )

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
        self.measurement = "mean"
        self.kpi_matrix = None

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

        button_frame = ttk.Frame(master=self.heatmap_selection)
        button_frame.pack(side=BOTTOM, pady=10)

        choose_min = tk.Button(button_frame, text="Min", command=self.select_min_measure)
        choose_min.pack(side=LEFT, padx=10, pady=10, fill=X)
        choose_mean = tk.Button(button_frame, text="Mean", command=self.select_mean_measure)
        choose_mean.pack(side=LEFT, padx=10, pady=10, fill=X)
        choose_max = tk.Button(button_frame, text="Max", command=self.select_max_measure)
        choose_max.pack(side=LEFT, padx=10, pady=10, fill=X)

        # Init heatmap frame with default heatmap (object interactions)
        key, heatmap_type = self.get_selected_heatmap_type()
        self.frame = HeatmapFrame(self.interior, key=key, heatmap_type=heatmap_type)
        self.frame.pack(fill=BOTH, expand=YES)

    def select_min_measure(self):
        self.measurement = "mean"
        key, heatmap_type = self.get_selected_heatmap_type()
        if key == "lagging_metrics":
            self.display_heatmap_lagging(self.kpi_matrix)
        elif key == "pooling_metrics":
            self.display_heatmap_pooling(self.kpi_matrix)
        else:
            return

    def select_mean_measure(self):
        self.measurement = "mean"
        key, heatmap_type = self.get_selected_heatmap_type()
        if key == "lagging_metrics":
            self.display_heatmap_lagging(self.kpi_matrix)
        elif key == "pooling_metrics":
            self.display_heatmap_pooling(self.kpi_matrix)
        else:
            return

    def select_max_measure(self):
        self.measurement = "max"
        key, heatmap_type = self.get_selected_heatmap_type()
        if key == "lagging_metrics":
            self.display_heatmap_lagging(self.kpi_matrix)
        elif key == "pooling_metrics":
            self.display_heatmap_pooling(self.kpi_matrix)
        else:
            return

    def on_open(self):
        # Compute OPerA KPIs. Argument `agg` can be changed to any of 'min', 'max' or 'mean'.
        # view().controller.run_task(key=TASK_OPERA, callback=self.display_opera, agg='mean')
        # Compute selected heatmap
        self.generate_heatmap()
        # view().controller.run_task(key=TASK_HEATMAP_OT, callback=self.display_heatmap_ot)

        view().show_toast(
            title="Insights into object and activity relation",
            message="In this tab, you can see several heatmaps visualising the relation between object types and between objecty types and activities. \n On the left, you can select between three different heatmaps. The purpose of every heatmap is explained in the tab. Just select one heatmap to start with an explore all of them step by step.",
            bootstyle="dark")

    def get_selected_heatmap_type(self):
        return list(HEATMAP_TYPES.items())[self.heatmap_selection_var.get()]

    def generate_heatmap(self):
        key, heatmap_type = self.get_selected_heatmap_type()
        print(f"Compute heatmap '{heatmap_type.title}'")
        heatmap_type.generate()
        # The above call schedules a task, with a callback that then displays the heatmap.

    def display_heatmap_ot(self, args):
        number_matrix, activities = args
        fig = go.Figure()
        fig.add_trace(go.Heatmap(z=number_matrix,
                                 x=list(number_matrix.columns.levels[0]),
                                 y=list(number_matrix.columns.levels[0]),
                                 hoverinfo='text',
                                 text=activities))
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()

    def refresh_heatmap_display(self):
        browser = self.frame.get_browser()
        if browser is not None:
            browser.Reload()
        else:
            print("Could not reload to show heatmap, browser is None")

    def display_heatmap_pooling(self, number_matrix):
        self.kpi_matrix = number_matrix
        number_matrix = number_matrix['pooling_time'][self.measurement]
        number_matrix.fillna(0, inplace=True)
        
        matrix=number_matrix
        hovertext = list()
        for x in matrix._stat_axis:
            hovertext.append(list())
            for y in matrix.columns:
                s = "In activity: " + str(x) + "<br>the first object of object type:  " + str(y) +"<br>gets delayed by: " + str(matrix[y][x]) + "days."
                hovertext[-1].append(s)
        
        fig = go.Figure()
        fig.add_trace(go.Heatmap(z=number_matrix,
                                 x=list(number_matrix.columns),
                                 y=list(number_matrix._stat_axis),
                                 hoverinfo='text',
                                 text=hovertext))
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()

    def display_heatmap_lagging(self, number_matrix):
        self.kpi_matrix = number_matrix
        number_matrix = number_matrix['lagging_time'][self.measurement]
        number_matrix.fillna(0, inplace=True)

        matrix=number_matrix
        hovertext = list()
        for x in matrix._stat_axis:
            hovertext.append(list())
            for y in matrix.columns:
                s = "In activity: " + str(x) + "<br>the first object of object type:  " + str(y) + "<br>gets delayed by: " + str(matrix[y][x]) + "days."
                hovertext[-1].append(s)

        fig = go.Figure()
        fig.add_trace(go.Heatmap(z=number_matrix,
                                 x=list(number_matrix.columns),
                                 y=list(number_matrix._stat_axis),
                                 hoverinfo='text',
                                 text=hovertext))
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()


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

        view().show_toast(
            title="Explore Process Executions and Variants",
            message="In this tab, you can see diferent executions of your process. All variants of executions are listed on the left by their frequency. By selcting them, you can see them in a graphical representation. Once you have discovered different executions of your process, you might also be interested in the whole process. Please click the perti net tab to discover a model of your whole process.",
            bootstyle='dark')

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

    def __init__(self, app, controller, window: tk.Tk):
        View.instance = self
        self.app = app
        self.controller = controller

        # Recycle the welcome screen's window (only one Tk instance per run)
        self.window = window
        Toast.window = window
        for w in self.window.winfo_children():
            w.destroy()
        self.window.title(f"{WINDOW_TITLE} - {app.file}")
        if self.app.get_preference("maximized"):
            self.window.state('zoomed')
        else:
            screen_size = (self.window.winfo_screenwidth(), self.window.winfo_screenheight())
            target_size = (1000, 600)
            size = (min(screen_size[0], target_size[0]), min(screen_size[1], target_size[1]))
            if size == screen_size:
                self.window.state("zoomed")
            else:
                self.window.geometry(f"{size[0]}x{size[1]}")
        self.window.resizable(width=True, height=True)
        self.resize_tracker = ResizeTracker(self.window, self.app)
        self.resize_tracker.bind_config()
        self.style.theme_use(self.app.get_preference("theme"))

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

    def show_toast(self, title, message, bootstyle=None):
        if not self.app.get_preference("show_demo_popups"):
            return
        logger.info(f"Demo message: {title}")
        toast = Toast(title=title, message=message, bootstyle=bootstyle, icon=None)
        toast.show_toast()

    def init_object_types(self, object_types, counts, model, colors=None):
        self.tab1.ot_widget = ObjectTypeWidget(self.tab1.ot_container, self, object_types, counts, model, colors)
        self.tab1.ot_widget.pack(fill=X)

    def init_activities(self, activities, model):
        self.tab1.act_widget = ActivityWidget(self.tab1.act_container, self, activities, model)
        self.tab1.act_widget.pack(fill=X)

    def init_ocel_df(self, model):
        self.tab1.init_table(model)

    def on_filter(self):
        self.tab1.table_widget.update_table()

    def change_theme(self, theme):
        logger.info(f"Change to theme '{theme}'")
        self.style.theme_use(theme)
        self.app.set_preference("theme", theme)

    @property
    def style(self) -> ttk.Style:
        return ttk.style.Style.instance
