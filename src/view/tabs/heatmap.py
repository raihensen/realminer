import tkinter as tk

import plotly.graph_objects as go
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from controller.export import Export
from controller.tasks import *
from view import utils
from view.components.tab import SidebarTab
from view.constants import *
from view.widgets.heatmap import HeatmapFrame, HeatmapType, HEATMAP_HTML_FILE

HEATMAP_TYPES = {
    "object_interactions": HeatmapType(title="Object Interactions",
                                       description=OBJECT_INTERACTIONS_DESCRIPTION, task=TASK_HEATMAP_OT,
                                       get_callback=lambda tab: tab.display_heatmap_ot),
    "pooling_metrics": HeatmapType(title="Pooling Metrics",
                                   description=POOLING_TIME_DESCRIPTION, task=TASK_HEATMAP_POOLING,
                                   get_callback=lambda tab: tab.display_heatmap_pooling),
    "lagging_metrics": HeatmapType(title="Lagging Metrics",
                                   description=LAGGING_TIME_DESCRIPTION, task=TASK_HEATMAP_LAGGING,
                                   get_callback=lambda tab: tab.display_heatmap_lagging)
}


class HeatMapTab(SidebarTab):
    def __init__(self, master, view):
        super().__init__(master=master,
                         view=view,
                         title="Heatmap",
                         sidebar_width_ratio=SIDEBAR_WIDTH_RATIO,
                         sidebar_min_width=SIDEBAR_MIN_WIDTH)
        self.display_label = ttk.Label(self.interior)
        self.measurement = "mean"
        self.kpi_matrix = None

        # Prepare heatmap types
        for heatmap_type in HEATMAP_TYPES.values():
            heatmap_type.controller = self.view.controller
            heatmap_type.callback = heatmap_type.get_callback(self)

        # Heatmap selection
        selection_info_label = ttk.Label(self.sidebar,
                                         wraplength=self.sidebar.winfo_width() - 20,
                                         text=HEAT_MAP_EXPLANATION)
        selection_info_label.bind('<Configure>',
                                  lambda e: selection_info_label.config(wraplength=self.sidebar.winfo_width() - 20))
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
        # self.view.controller.run_task(key=TASK_OPERA, callback=self.display_opera, agg='mean')
        # Compute selected heatmap
        self.generate_heatmap()
        # self.view.controller.run_task(key=TASK_HEATMAP_OT, callback=self.display_heatmap_ot)

        self.view.show_toast(title="Insights into object and activity relation", message=TAB_EXPLANATION_HEATMAP,
                             bootstyle="dark")

    def get_selected_heatmap_type(self):
        return list(HEATMAP_TYPES.items())[self.heatmap_selection_var.get()]

    def generate_heatmap(self):
        key, heatmap_type = self.get_selected_heatmap_type()
        print(f"Compute heatmap '{heatmap_type.title}'")
        heatmap_type.generate()
        # The above call schedules a task, with a callback that then displays the heatmap.
        self.frame.update_description(heatmap_type)

    def display_heatmap_ot(self, args):
        number_matrix, activities = args
        fig = go.Figure()
        # TODO add margin to fig
        fig.add_trace(go.Heatmap(z=number_matrix,
                                 x=list(number_matrix.columns.levels[0]),
                                 y=list(number_matrix.columns.levels[0]),
                                 hoverinfo='text',
                                 text=activities))
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()
        self.view.controller.current_export = Export("heatmap_object_types", "html", copy_from_path=HEATMAP_HTML_FILE,
                                                     use_dialog=True)

    def refresh_heatmap_display(self):
        browser = self.frame.get_browser()
        if browser is not None:
            browser.Reload()
        else:
            print("Could not reload to show heatmap, browser is None")

    def display_heatmap_pooling(self, number_matrix):
        self.kpi_matrix = number_matrix
        number_matrix = number_matrix['pooling_time'][self.measurement]
        tmin, tmax = max(0, number_matrix.min().min()), number_matrix.max().max()
        number_matrix.fillna(max(0 - .2 * (tmax - tmin), -1), inplace=True)

        matrix = number_matrix
        hovertext = list()
        for x in matrix._stat_axis:
            hovertext.append(list())
            for y in matrix.columns:
                time_str = utils.time_formatter(matrix[y][x])
                if time_str is not None:
                    s = f"Before executing '{x}'<br>the objects of type '{y}'<br>take {time_str} for pooling"
                else:
                    s = f"The object type '{y}'<br>is not related to '{x}'"
                hovertext[-1].append(s)

        fig = go.Figure()
        heatmap = go.Heatmap(z=number_matrix,
                             x=list(number_matrix.columns),
                             y=list(number_matrix._stat_axis),
                             hoverinfo='text',
                             text=hovertext)
        self.format_heatmap_time_intervals(heatmap, tmin, tmax)
        fig.add_trace(heatmap)
        fig.update_layout(margin_b=200, margin_r=120)
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()
        self.view.controller.current_export = Export("heatmap_pooling", "html", copy_from_path=HEATMAP_HTML_FILE,
                                                     use_dialog=True)

    def display_heatmap_lagging(self, number_matrix):
        self.kpi_matrix = number_matrix
        number_matrix = number_matrix['lagging_time'][self.measurement]
        tmin, tmax = max(0, number_matrix.min().min()), number_matrix.max().max()
        number_matrix.fillna(min(0 - .2 * (tmax - tmin), -1), inplace=True)

        matrix = number_matrix
        hovertext = list()
        for x in matrix._stat_axis:
            hovertext.append(list())
            for y in matrix.columns:
                time_str = utils.time_formatter(matrix[y][x])
                if time_str is not None:
                    s = f"The last object of type '{y}'<br>delays the activity '{x}'<br>by " + time_str
                else:
                    s = f"The object type '{y}'<br>is not related to '{x}'"
                hovertext[-1].append(s)

        fig = go.Figure()
        heatmap = go.Heatmap(z=number_matrix,
                             x=list(number_matrix.columns),
                             y=list(number_matrix._stat_axis),
                             hoverinfo='text',
                             text=hovertext)
        self.format_heatmap_time_intervals(heatmap, tmin, tmax)
        fig.add_trace(heatmap)
        fig.update_layout(margin_b=200, margin_r=120)
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()
        self.view.controller.current_export = Export("heatmap_lagging", "html", copy_from_path=HEATMAP_HTML_FILE,
                                                     use_dialog=True)

    @staticmethod
    def format_heatmap_time_intervals(heatmap, tmin, tmax):
        # Set the custom tick values and labels for the colorbar
        heatmap.colorbar.tickvals = [tmin, tmax]
        heatmap.colorbar.ticktext = [utils.time_formatter(t) for t in (tmin, tmax)]
