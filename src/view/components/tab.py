
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkfontawesome import icon_to_image as fontawesome


class Tabs(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.tabs = []
        # self.callbacks = []
        self.active_tab = None
        self.notebook = ttk.Notebook(master=self, padding=0)
        self.notebook.pack(fill=BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def add_tab(self, tab, **kwargs):
        # tab = Tab(master=self.notebook, **kwargs)
        tab.pack(fill=BOTH, expand=True)
        tab_args = {
            "text": tab.title,
            "sticky": NSEW
        }
        if tab.icon is not None:
            tab_args["icon"] = fontawesome(tab.icon, fill="grey", scale_to_height=15)
            tab_args["compound"] = LEFT

        self.notebook.add(tab, **tab_args)
        self.tabs.append(tab)
        # self.callbacks.append((on_open, on_close))
        return tab

    def on_tab_change(self, e):
        index = self.notebook.index(self.notebook.select())
        new_tab = self.tabs[index]
        new_tab.on_open()
        if self.active_tab is not None:
            self.active_tab.on_close()
        self.active_tab = new_tab

        # callback_open = self.callbacks[index][0]
        # if callback_open is not None:
        #     callback_open()
        # if self.active_tab is not None:
        #     callback_close = self.callbacks[self.active_tab][1]
        #     if callback_close is not None:
        #         callback_close()
        # self.active_tab = index


class Tab(ttk.Frame):
    def __init__(self, master: Tabs, title: str, icon=None, **kwargs):
        super().__init__(master=master.notebook, **kwargs)
        self.title = title
        self.icon = icon

    def on_open(self):
        pass

    def on_close(self):
        pass



