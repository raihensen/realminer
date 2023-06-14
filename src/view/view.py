import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from tkfontawesome import icon_to_image as fontawesome
from PIL import Image, ImageTk
import os

# from view.components.scrollable_frame import VerticalScrolledFrame
from view.components.accordion import Accordion
from view.widgets.object_types import ObjectTypeWidget
from view.widgets.activities import ActivityWidget
from view.components.tab import Tabs, Tab
# from controller.controller import *

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


class SidebarTab(Tab):
    def __init__(self, master, title, **kwargs):
        super().__init__(master=master, title=title, **kwargs)
        # Main layout
        self.rowconfigure(0, minsize=TOOLBAR_HEIGHT)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, minsize=SIDEBAR_MIN_WIDTH, weight=1)
        self.columnconfigure(1, minsize=SIDEBAR_MIN_WIDTH / SIDEBAR_WIDTH_RATIO,
                             weight=int(round(1 / SIDEBAR_WIDTH_RATIO, 0)) - 1)

        view().style.configure("sidebar.TFrame", background="#e0e0e0")
        # self.sidebar = VerticalScrolledFrame(master=self.window, style="sidebar.TFrame")
        self.sidebar = ScrolledFrame(master=self)
        self.sidebar.grid(row=1, column=0, sticky=NSEW)
        self.main = tk.Frame(master=self)
        self.main.grid(row=1, column=1, sticky=NSEW)
        self.interior = self.main


class FilterTab(SidebarTab):
    def __init__(self, master):
        super().__init__(master=master, title="Filters and Settings")

        # Sidebar contents
        acc = Accordion(self.sidebar, title_height=50, bootstyle=SECONDARY)
        acc.pack(side=TOP, fill=X)
        # Object types
        self.ot_container = acc.add_chord(title='Object types', expanded=True)
        self.ot_widget = None
        # Activities
        self.act_container = acc.add_chord(title='Activities')
        self.act_widget = None
        # tk.Label(self.act_container, text='hello world', bg='white').pack()

        # get ocpa ocel
        self.ocpa_button = tk.Button(master=self.main, text="Get ocpa ocel", command=view().controller.model.get_opca_ocel)
        self.ocpa_button.pack()

    def on_open(self):
       pass


class PetriNetTab(Tab):
    def __init__(self, master):
        super().__init__(master=master, title="Petri Net")

        # Petri Net Discovery
        self.pn_button = tk.Button(master=self, text="Discover Petri Net", command=self.display_petri_net)
        self.pn_button.pack()

    def on_open(self):
        self.display_petri_net()

    def display_petri_net(self):
        # TODO move to controller, with callback
        # TODO display in window
        logger.info("Discovering petri net")
        view().controller.model.ocel.discover_petri_net()
        ocpn_image = Image.open('static/img/ocpn.png')
        image_tk = ImageTk.PhotoImage(ocpn_image)
        # label = ttk.Label(self.window, text="Petri Net", image=image_tk)
        # label.grid(row=2, column=0, sticky='nsew')
        # label.pack()


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
        self.tab_widget.pack(side=TOP, fill=BOTH)

        # create a new frame
        self.tab1 = FilterTab(self.tab_widget)
        self.tab_widget.add_tab(self.tab1)
        self.tab2 = PetriNetTab(self.tab_widget)
        self.tab_widget.add_tab(self.tab2)

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

    def init_activities(self, activities, model, colors=None):
        self.activities_widget = ActivityWidget(self.tab1.act_container, activities, model, colors)
        self.activities_widget.pack(fill=X)

    def change_theme(self, theme):
        logger.info(f"Change to theme '{theme}'")
        self.style.theme_use(theme)

    def test_set_label(self, x):
        self.test_label.config(text=str(x))

    @property
    def style(self):
        return ttk.style.Style.instance

    def start(self):
        self.window.mainloop()

