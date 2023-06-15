import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import random

from view.components.dnd_list import DndList, DndListItem

logger = logging.getLogger("app_logger")


class ActivityWidget(ttk.Frame):
    def __init__(self, master, activities, model, **kwargs):
        super().__init__(master=master, **kwargs)

        self.list_widget = ActivityListWidget(master=self, activities=activities, colors=None, on_swap=self.on_swap)
        self.list_widget.pack(side=TOP, fill=X)

        btn_frame = ttk.Frame(master=self)
        btn_frame.pack(side=TOP, fill=X, padx=20, pady=10)

        self.btn_apply = ttk.Button(master=btn_frame, text="Apply", bootstyle=PRIMARY, command=self.apply)
        self.btn_reset = ttk.Button(master=btn_frame, text="Reset", bootstyle=SECONDARY, command=self.reset)

        self.btn_reset.pack(side=RIGHT)
        self.btn_apply.pack(side=RIGHT, padx=10)

        self.model = model

    def on_swap(self, order):
        logger.info(f"Activities reordered: {order}")
        self.update_buttons()

    def apply(self):
        active_activities = self.get_list_of_active_activities()
        self.model.update_active_activities_in_model(active_activities)
        logger.debug("Apply - Activities")


    def reset(self):
        for activity in self.children['!activitylistwidget'].items:
            activity.checkbox_var.set(1)
        active_activities = self.get_list_of_active_activities()
        self.model.update_active_activities_in_model(active_activities)
        logger.debug("Reset - Activities")

    def get_list_of_active_activities(self):
        active_activities = [activity.item for activity in self.children['!activitylistwidget'].items if activity.checkbox_var.get()]
        logger.info("The active activities are: " + str(active_activities))
        return active_activities


class ActivityListWidget(DndList):
    def __init__(self, master, activities, on_swap=None, **kwargs):
        super().__init__(master, on_swap=on_swap, **kwargs)

        for activity in activities:
            self.add_item(item=activity, child=ActivityEntryWidget(master=self,
                                                               activity=activity,
                                                               enabled=True))

class ActivityEntryWidget(DndListItem):
    def __init__(self, master, activity: str, enabled: bool, **kwargs):
        super().__init__(master=master, item=activity, **kwargs)

        # checkbox and name
        self.checkbox_var = tk.IntVar(value=int(enabled))
        self.checkbox = ttk.Checkbutton(master=self.interior,
                                        text=f"{activity}",
                                        command=self.update_activity_checkbox,
                                        variable=self.checkbox_var,
                                        bootstyle="round-toggle")
        self.checkbox.pack(side=LEFT)

    def update_activity_checkbox(self):
        activity_status = self.checkbox_var.get()
        item_status = 'on' if activity_status else 'off'
        logging.info(f"Activity: {self.item} was toggled: {item_status}")

    def is_checked(self):
        return bool(self.checkbox_var.get())
