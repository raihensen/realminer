
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from view.constants import *
from view.utils import ResizeTracker
from view.widgets.object_types import ObjectTypeWidget
from view.widgets.activities import ActivityWidget
from view.components.tab import Tabs
from view.widgets.popups import Toast

from view.tabs.filters_settings import FilterTab
from view.tabs.variants import VariantsTab
from view.tabs.petrinet import PetriNetTab
from view.tabs.heatmap import HeatMapTab

from controller.tasks import *
from controller.export import Export

logger = logging.getLogger("app_logger")


def view():
    return View.instance


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

        # Init tabs
        self.tab_widget = Tabs(master=self.window)
        self.tab_widget.pack(side=TOP, fill=BOTH, expand=True)
        self.tab1 = FilterTab(self.tab_widget, self)
        self.tab_widget.add_tab(self.tab1)
        self.tab4 = VariantsTab(self.tab_widget, self)
        self.tab_widget.add_tab(self.tab4)
        self.tab2 = PetriNetTab(self.tab_widget, self)
        self.tab_widget.add_tab(self.tab2)
        self.tab3 = HeatMapTab(self.tab_widget, self)
        self.tab_widget.add_tab(self.tab3)

        # Init key events
        self.window.bind("<Control-s>", lambda *args: self.trigger_export())

    def trigger_export(self, name=None):
        self.controller.trigger_export(name)

    def show_toast(self, title, message, bootstyle=None):
        if not self.app.get_preference("show_demo_popups"):
            return
        logger.info(f"Demo message: {title}")
        toast = Toast(title=title, message=message, bootstyle=bootstyle, icon="")
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
