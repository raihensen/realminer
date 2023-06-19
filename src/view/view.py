import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkfontawesome import icon_to_image as fontawesome
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

# from view.components.scrollable_frame import VerticalScrolledFrame
from view.components.accordion import Accordion
from view.widgets.object_types import ObjectTypeWidget
from view.widgets.activities import ActivityWidget
from view.components.tab import Tabs, Tab, SidebarTab
from view.components.zoomable_frame import AdvancedZoom
from controller.tasks import *

# from ocpa_variants import *

WINDOW_TITLE = "Object-centric Business App"
if os.getlogin() == "RH":
    MAXIMIZED = True
else:
    MAXIMIZED = False
SIDEBAR_WIDTH_RATIO = 0.2
SIDEBAR_MIN_WIDTH = 150
TOOLBAR_HEIGHT = 40

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
        # tk.Label(self.act_container, text='hello world', bg='white').pack()

    def on_open(self):
        pass


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


class HeatMapTab(Tab):
    def __init__(self, master):
        super().__init__(master=master, title="Heatmap")
        self.image_tk = None
        self.display_label = None

    def on_open(self):
        # self.display_heatmap_ot()
        view().controller.run_task(key=TASK_HEATMAP_OT, callback=self.display_heatmap_ot)

    def display_heatmap_ot(self, number_matrix):
        figure = plt.figure()
        sns.heatmap(number_matrix, cmap="crest")
        plt.show()
        # TODO remove plt.show() and make sure no (invisible) window is opened


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


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        if MAXIMIZED:
            self.state('zoomed')


class View:
    instance = None

    def __init__(self, controller, theme):
        View.instance = self
        self.controller = controller
        self.window = Window()

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

    def change_theme(self, theme):
        logger.info(f"Change to theme '{theme}'")
        self.style.theme_use(theme)

    @property
    def style(self):
        return ttk.style.Style.instance

    def start(self):
        self.window.mainloop()
