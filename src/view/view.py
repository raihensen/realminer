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

        # get ocpa ocel
        self.ocpa_button = tk.Button(master=self.main, text="Test OCPA functions", command=self.test_ocpa)
        self.ocpa_button.pack()

    def on_open(self):
        pass

    def test_ocpa(self):
        print(view().controller.model.object_types)
        print(view().controller.model.cases)


class PetriNetTab(Tab):
    def __init__(self, master):
        super().__init__(master=master, title="Petri Net")
        self.display_label = ttk.Label(self)
        self.imgview = None

        # Petri Net Discovery
        # self.pn_button = tk.Button(master=self, text="Discover Petri Net", command=self.generate_petri_net)
        # self.pn_button.pack()

    def on_open(self):
        view().controller.run_task(key=TASK_DISCOVER_PETRI_NET, callback=self.display_petri_net)

    def display_petri_net(self, path):
        # image = Image.open(path)
        # w0, h0 = image.size
        # aspect = w0 / h0
        # w = self.winfo_width() - 20
        # h = int(w / aspect)
        # image = image.resize((w, h))
        # logger.info(f"Resize image to {w}x{h}")
        # self.ocpn_image = ImageTk.PhotoImage(image)
        # self.display_label.pack_forget()
        # self.display_label = ttk.Label(master=self, image=self.ocpn_image)
        # self.display_label.pack()
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

        # filename = 'static/img/heatmap.png'
        # plt.savefig(filename, dpi=dpi)
        # logger.info("saved heatmap as png")
        # return filename

        # print("[display]")
        # heatmap_image = Image.open(path)
        # self.image_tk = ImageTk.PhotoImage(heatmap_image)
        # if self.display_label is not None:
        #     self.display_label.pack_forget()
        # self.display_label = ttk.Label(self, image=self.image_tk)
        # self.display_label.pack()

class VariantsTab(Tab):
    def __init__(self, master):
        super().__init__(master=master, title="Variants Explorer")
        self.image_tk = None
        self.display_label = None

        variants = self.compute_variants()
        keys = variants.keys()
        print_variants = []
        for key in keys:
            print_variants.append(key)
        tuple = self.compute_basic_stats()
        num_proc = tuple[0]
        num_var = tuple[1]
 
        self.stats_label = tk.Label(self, text="There are "+ str(num_proc) +" process executions of "+ str(num_var) +" varinats. In the Drop down menu below, these variants are listed by theire frequency (descending).")
        self.stats_label.pack()

        self.Combo = ttk.Combobox(self, values = print_variants, width=30)
        self.Combo.set("Pick a Variant")
        self.Combo.pack(padx = 5, pady = 5)

        # label of basic statistics
        #tuple = self.computeBasicVariantStats()
        #num_proc_exe = tuple[0]
        #num_var = tuple[1]
        self.show_button = tk.Button(master=self, text="Show Variant", command=self.display_variants)
        self.show_button.pack()

    def on_open(self):
        pass

    # def compute_basic_stats(self):
    #     tuple = get_basic_stats()
    #     return tuple
    #
    # def compute_variants(self):
    #     logger.info("Computing Variants")
    #     variants = get_variants()
    #     return variants
    # def display_variants(self):
    #     #print('test')
    #     graph = display_variant(self.compute_variants()[self.Combo.get()])
    #     #figure = plt.figure()
    #     #nx.draw_networkx(graph)
    #     #plt.show()
    #     # TODO remove plt.show() and make sure no (invisible) window is opened


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
        # self.tab4 = VariantsTab(self.tab_widget)
        # self.tab_widget.add_tab(self.tab4)

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

