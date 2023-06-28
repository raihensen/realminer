import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkfontawesome import icon_to_image as fontawesome
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px

from cefpython3 import cefpython as cef
import ctypes

# from view.components.scrollable_frame import VerticalScrolledFrame
from view.constants import *
from view.components.accordion import Accordion
from view.widgets.object_types import ObjectTypeWidget
from view.widgets.activities import ActivityWidget
from view.widgets.heatmap import *
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


IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"

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

        # Display event log as table (https://ilya-fradlin.atlassian.net/browse/CO-23)

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
        self.display_label = ttk.Label(self)
        self.imgview = None

        self.frame= MainFrame(self)
        self.frame.pack()

    def on_open(self):
        view().controller.run_task(key=TASK_HEATMAP_OT, callback=self.display_heatmap_ot)

    def display_heatmap_ot(self, number_matrix):
        print(number_matrix)
        fig = go.Figure()
        fig.add_trace(go.Heatmap(z=number_matrix, x=list(number_matrix.columns.levels[0]), y=list(number_matrix.columns.levels[0])))#, x=number_matrix.index.values.tolist(), y=number_matrix.index.values.tolist()))
        fig.write_html(HEATMAP_HTML_FILE)
        # refresh browser
        browser = self.frame.get_browser()
        if browser is not None:
            browser.Reload()
        else:
            print("Could not reload to show heatmap, browser is None")


class MainFrame(tk.Frame):
    def __init__(self, root):
        self.browser_frame = None
        # self.navigation_bar = None

        # Root
        #root.geometry("900x640")
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)

        # MainFrame
        tk.Frame.__init__(self, root)
        #self.master.title("Tkinter example")
        #self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        #self.master.bind("<Configure>", self.on_root_configure)
        self.setup_icon()
        self.bind("<Configure>", self.on_configure)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        # NavigationBar
        # self.navigation_bar = NavigationBar(self)
        # self.navigation_bar.grid(row=0, column=0,
        #                          sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 0, weight=0)
        tk.Grid.columnconfigure(self, 0, weight=0)

        # BrowserFrame
        self.browser_frame = BrowserFrame(self, navigation_bar=None)
        self.browser_frame.grid(row=1, column=0,
                                sticky=(tk.N + tk.S + tk.E + tk.W))
        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        # Pack MainFrame
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def on_root_configure(self, _):
        logger.debug("MainFrame.on_root_configure")
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        logger.debug("MainFrame.on_configure")
        if self.browser_frame:
            width = event.width
            height = event.height
            # if self.navigation_bar:
            #     height = height - self.navigation_bar.winfo_height()
            self.browser_frame.on_mainframe_configure(width, height)

    def on_focus_in(self, _):
        logger.debug("MainFrame.on_focus_in")

    def on_focus_out(self, _):
        logger.debug("MainFrame.on_focus_out")

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
        self.master.destroy()

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

    def setup_icon(self):
        resources = os.path.join(os.path.dirname(__file__), "resources")
        icon_path = os.path.join(resources, "tkinter"+IMAGE_EXT)
        if os.path.exists(icon_path):
            self.icon = tk.PhotoImage(file=icon_path)
            # noinspection PyProtectedMember
            self.master.call("wm", "iconphoto", self.master._w, self.icon)


class NavigationBar(tk.Frame):
    def __init__(self, master):
        self.back_state = tk.NONE
        self.forward_state = tk.NONE
        self.back_image = None
        self.forward_image = None
        self.reload_image = None

        tk.Frame.__init__(self, master)
        resources = os.path.join(os.path.dirname(__file__), "resources")

        # Back button
        back_png = os.path.join(resources, "back"+IMAGE_EXT)
        if os.path.exists(back_png):
            self.back_image = tk.PhotoImage(file=back_png)
        self.back_button = tk.Button(self, text="Backward",
                                     command=self.go_back)
        self.back_button.grid(row=0, column=0)

        # Forward button
        forward_png = os.path.join(resources, "forward"+IMAGE_EXT)
        if os.path.exists(forward_png):
            self.forward_image = tk.PhotoImage(file=forward_png)
        self.forward_button = tk.Button(self, text="Forward",
                                        command=self.go_forward)
        self.forward_button.grid(row=0, column=1)

        # Reload button
        reload_png = os.path.join(resources, "reload"+IMAGE_EXT)
        if os.path.exists(reload_png):
            self.reload_image = tk.PhotoImage(file=reload_png)
        self.reload_button = tk.Button(self, text="Reload",
                                       command=self.reload)
        self.reload_button.grid(row=0, column=2)

        # Url entry
        self.url_entry = tk.Entry(self)
        self.url_entry.bind("<FocusIn>", self.on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self.on_url_focus_out)
        self.url_entry.bind("<Return>", self.on_load_url)
        self.url_entry.bind("<Button-1>", self.on_button1)
        self.url_entry.grid(row=0, column=3,
                            sticky=(tk.N + tk.S + tk.E + tk.W))
        # tk.Grid.rowconfigure(self, 0, weight=100)
        tk.Grid.columnconfigure(self, 3, weight=1)

        # Update state of buttons
        self.update_state()

    def go_back(self):
        pass

    def go_forward(self):
        pass

    def reload(self):
        if self.master.get_browser():
            self.master.get_browser().Reload()

    def set_url(self, url):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)

    def on_url_focus_in(self, _):
        logger.debug("NavigationBar.on_url_focus_in")

    def on_url_focus_out(self, _):
        logger.debug("NavigationBar.on_url_focus_out")

    def on_load_url(self, _):
        if self.master.get_browser():
            self.master.get_browser().StopLoad()
            self.master.get_browser().LoadUrl(self.url_entry.get())

    def on_button1(self, _):
        """Fix CEF focus issues (#255). See also FocusHandler.OnGotFocus."""
        logger.debug("NavigationBar.on_button1")
        self.master.master.focus_force()

    def update_state(self):
        pass


class BrowserFrame(tk.Frame):
    def __init__(self, master, navigation_bar=None):
        print("init BrowserFrame")
        self.navigation_bar = navigation_bar
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, master)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        self.focus_set()

    def embed_browser(self):
        print("embed browser")
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info,
                                             url=f"file:///{HEATMAP_HTML_FILE}") #todo, C:\Users\kimam\Documents\studium\3_master\praktikum\pads-x-celonis-ocpm
        assert self.browser, "Browser could not be initialized"
        self.browser.SetClientHandler(LoadHandler(self))
        self.browser.SetClientHandler(FocusHandler(self))
        self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        print("configuring")
        if not self.browser:
            print("configuring if")
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            ctypes.windll.user32.SetWindowPos(
                self.browser.GetWindowHandle(), 0,
                0, 0, width, height, 0x0002)
            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        logger.debug("BrowserFrame.on_focus_in")
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        logger.debug("BrowserFrame.on_focus_out")
        if self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        self.destroy()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None


class LoadHandler(object):
    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    #def OnLoadStart(self, browser, **_):
        #if self.browser_frame.master.navigation_bar:
        #    self.browser_frame.master.navigation_bar.set_url(browser.GetUrl())


class FocusHandler(object):
    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnTakeFocus(self, next_component, **_):
        logger.debug("FocusHandler.OnTakeFocus, next={next}"
                     .format(next=next_component))

    def OnSetFocus(self, source, **_):
        logger.debug("FocusHandler.OnSetFocus, source={source}"
                     .format(source=source))
        return False

    def OnGotFocus(self, **_):
        """Fix CEF focus issues (#255). Call browser frame's focus_set
           to get rid of type cursor in url entry widget."""
        logger.debug("FocusHandler.OnGotFocus")
        self.browser_frame.focus_set()


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

    def change_theme(self, theme):
        logger.info(f"Change to theme '{theme}'")
        self.style.theme_use(theme)

    @property
    def style(self):
        return ttk.style.Style.instance

    def start(self):
        cef.Initialize()
        # self.window.mainloop()
        cef.Shutdown()
