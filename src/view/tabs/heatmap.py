
import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from view.constants import *
from view.components.tab import Tabs, Tab, SidebarTab
from controller.tasks import *
from controller.export import Export
from view.widgets.heatmap import HeatmapFrame, HeatmapType, HEATMAP_HTML_FILE
import plotly.graph_objects as go


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

        self.view.show_toast(title="Insights into object and activity relation", message=TAB_EXPLANATION_HEATMAP, bootstyle="dark")

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
        tmin, tmax = number_matrix.min().min(), number_matrix.max().max()

        matrix = number_matrix
        hovertext = list()
        for x in matrix._stat_axis:
            hovertext.append(list())
            for y in matrix.columns:
                s = f"In activity: {x}<br>Pooling the objects of type:  {y}<br>needs: " + HeatMapTab.time_formatter(matrix[y][x])
                hovertext[-1].append(s)

        fig = go.Figure()
        heatmap = go.Heatmap(z=number_matrix,
                             x=list(number_matrix.columns),
                             y=list(number_matrix._stat_axis),
                             hoverinfo='text',
                             text=hovertext)
        self.format_heatmap_time_intervals(heatmap, tmin, tmax)
        fig.add_trace(heatmap)
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()

    def display_heatmap_lagging(self, number_matrix):
        self.kpi_matrix = number_matrix
        number_matrix = number_matrix['lagging_time'][self.measurement]
        number_matrix.fillna(0, inplace=True)
        tmin, tmax = number_matrix.min().min(), number_matrix.max().max()

        matrix = number_matrix
        hovertext = list()
        for x in matrix._stat_axis:
            hovertext.append(list())
            for y in matrix.columns:
                s = f"In activity: {x}<br>the first object of object type:  {y}<br>gets delayed by: " + HeatMapTab.time_formatter(matrix[y][x])
                hovertext[-1].append(s)

        fig = go.Figure()
        heatmap = go.Heatmap(z=number_matrix,
                             x=list(number_matrix.columns),
                             y=list(number_matrix._stat_axis),
                             hoverinfo='text',
                             text=hovertext)
        self.format_heatmap_time_intervals(heatmap, tmin, tmax)
        fig.add_trace(heatmap)
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        self.refresh_heatmap_display()

    @staticmethod
    def time_formatter(t) -> str:
        if t >= 60 * 60 * 24 * 365:
            return f'{t / (60 * 60 * 24 * 365):.1f}y'
        elif t >= 60 * 60 * 24:
            return f'{t / (60 * 60 * 24):.1f}d'
        elif t >= 60 * 60:
            hours = int(t // (60 * 60))
            minutes = str(int((t // 60) % 60)).ljust(2, '0')
            return f"{hours}:{minutes}h"
        elif t >= 60:
            minutes = str(int(t // 60)).ljust(2, '0')
            seconds = str(int(t % 60)).ljust(2, '0')
            return f'0:{minutes}:{seconds}'
        elif t > 0:
            return f'{t:.1f}s'
        else:
            return "0d"

    @staticmethod
    def format_heatmap_time_intervals(heatmap, tmin, tmax):
        # Set the custom tick values and labels for the colorbar
        heatmap.colorbar.tickvals = [tmin, tmax]
        heatmap.colorbar.ticktext = [HeatMapTab.time_formatter(t) for t in (tmin, tmax)]