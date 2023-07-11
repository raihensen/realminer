
import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from view.constants import *
from view.components.tab import Tabs, Tab, SidebarTab
from controller.tasks import *
from controller.export import Export
from view.components.zoomable_frame import AdvancedZoom


class PetriNetTab(Tab):
    def __init__(self, master, view):
        super().__init__(master=master, view=view, title="Petri Net")
        self.display_label = ttk.Label(self)
        self.imgview = None

    def on_open(self):
        self.view.controller.run_task(key=TASK_DISCOVER_PETRI_NET, callback=self.display_petri_net, bgcolor=ttk.Style.instance.colors.bg)
        self.view.show_toast(title="Process model discovery", message=TAB_EXPLANATION_PETRI_NET, bootstyle='dark')

    def display_petri_net(self, path):
        if self.imgview is not None:
            self.imgview.canvas.forget()
            self.imgview.forget()
        self.imgview = AdvancedZoom(self, path=path)
        self.imgview.pack(fill=BOTH, expand=True)
        self.view.controller.current_export = Export("petrinet", "png", copy_from_path=path, use_dialog=True)
