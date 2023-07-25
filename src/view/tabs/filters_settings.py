
import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from view.constants import *
from view.components.tab import Tabs, Tab, SidebarTab
from controller.tasks import *
from controller.export import Export
from view.components.accordion import Accordion
from view.widgets.table_view import TableViewWidget
import functools


class FilterTab(SidebarTab):
    def __init__(self, master, view):
        super().__init__(master=master,
                         view=view,
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
        self.checkbox_demo_popups_var = tk.IntVar(value=int(self.view.app.get_preference("show_demo_popups")))
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
        theme_var = tk.StringVar(value=self.view.app.get_preference("theme"))
        for theme in ttk.style.STANDARD_THEMES:
            theme_menu.add_radiobutton(label=theme,
                                       variable=theme_var,
                                       command=lambda t=theme: self.view.change_theme(t))
        theme_menubutton["menu"] = theme_menu
        # Table
        self.table_widget = None
        self.export_table_button = None

    def update_demo_popups_checkbox(self):
        state = bool(self.checkbox_demo_popups_var.get())
        self.view.app.set_preference("show_demo_popups", state)

    def on_open(self):
        if self.table_widget is not None:
            self.table_widget.update_table()
        self.view.show_toast(title="Welcome to REAL MINER", message=TAB_EXPLANATION_FILTERS_SETTINGS, bootstyle="dark")

    def init_table(self, model):
        self.table_widget = TableViewWidget(self.interior, self.view.controller, model)
        button_row = ttk.Frame(master=self.interior)
        button_row.pack(side=BOTTOM, fill=X)
        export_jsonocel_button = ttk.Button(master=button_row,
                                            text="Export (.jsonocel)",
                                            command=functools.partial(self.view.trigger_export, "event_log_jsonocel"))
        export_jsonocel_button.pack(side=RIGHT, padx=10, pady=10)
        export_csv_button = ttk.Button(master=button_row,
                                       text="Export (.csv)",
                                       command=functools.partial(self.view.trigger_export, "event_log_csv"))
        export_csv_button.pack(side=RIGHT, padx=10, pady=10)
