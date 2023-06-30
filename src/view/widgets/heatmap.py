
import os
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from cefpython3 import cefpython as cef
import ctypes

import logging
from controller.tasks import *

logger = logging.getLogger("app_logger")

HEATMAP_HTML_FILE = "tmp/heatmap.html"
IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"


class HeatmapType:
    def __init__(self, title, description, task, get_callback, **kwargs):
        self.title = title
        self.description = description
        self.task = task
        self.task_kwargs = kwargs
        self.get_callback = get_callback
        self.generator = None
        self.callback = None
        self.controller = None

    def generate(self):
        if self.controller is not None and self.callback is not None:
            self.controller.run_task(key=self.task, callback=self.callback, *self.task_kwargs)


class HeatmapFrame(tk.Frame):
    def __init__(self, master, key: str, heatmap_type: HeatmapType):
        tk.Frame.__init__(self, master)
        self.bind("<Configure>", self.on_configure)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        # Title and Description
        style = ttk.Style()
        style.configure('title.TLabel', font=(None, 18, 'bold'))
        style.configure('description.TLabel', font=(None, 10))
        padx = 10
        self.title = ttk.Label(master=self, text=heatmap_type.title, style="title.TLabel")
        self.title.pack(side=TOP, padx=padx, pady=10, fill=X)
        self.description = tk.Message(self, width=self.winfo_width() - 2 * padx, anchor=W, text=heatmap_type.description)
        self.description.pack(side=TOP, padx=padx, fill=X)

        # BrowserFrame
        self.browser_frame = BrowserFrame(self, navigation_bar=None)
        self.browser_frame.pack(side=TOP, fill=BOTH, expand=YES, padx=10, pady=10)

    def update_description(self, heatmap_type):
        self.description.config(text=heatmap_type.description)


    def on_root_configure(self, _):
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        if self.browser_frame:
            width = event.width
            height = event.height
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
        cef.Initialize()
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url=f"file:///{HEATMAP_HTML_FILE}")
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


