import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import random

from view.components.dnd_list import DndList, DndListItem
from pm4py.visualization.ocel.ocpn.variants.wo_decoration import ot_to_color

logger = logging.getLogger("app_logger")


class ObjectTypeWidget(ttk.Frame):
    def __init__(self, master, view, object_types, counts, model, colors=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.view = view

        self.list_widget = ObjectTypeListWidget(master=self, object_types=object_types, counts=counts, colors=None)
        self.list_widget.pack(side=TOP, fill=X)

        btn_frame = ttk.Frame(master=self)
        btn_frame.pack(side=TOP, fill=X, padx=20, pady=10)

        self.btn_apply = ttk.Button(master=btn_frame, text="Apply", bootstyle=PRIMARY, command=self.apply)
        self.btn_reset = ttk.Button(master=btn_frame, text="Reset", bootstyle=SECONDARY, command=self.reset)

        self.btn_reset.pack(side=RIGHT)
        self.btn_apply.pack(side=RIGHT, padx=10)

        self.model = model

    def apply(self):
        active_objects = self.get_list_of_active_objects()
        self.model.update_active_ot_in_model(active_objects)
        logger.debug("Apply")
        self.view.on_filter()

    def reset(self):
        for ot in self.children['!objecttypelistwidget'].items:
            ot.checkbox_var.set(1)
        active_objects = self.get_list_of_active_objects()
        self.model.update_active_ot_in_model(active_objects)
        logger.debug("Reset")
        self.view.on_filter()

    def get_list_of_active_objects(self):
        active_objects = [ot.item for ot in self.children['!objecttypelistwidget'].items if ot.checkbox_var.get()]
        logger.info("The active objects are: " + str(active_objects))
        return active_objects


class ObjectTypeListWidget(DndList):
    def __init__(self, master, object_types, counts, colors=None, on_swap=None, **kwargs):
        super().__init__(master, on_swap=on_swap, **kwargs)

        # TODO random color assignment, use nice color palette
        if colors is None:
            colors = {ot: ot_to_color(ot) for ot in object_types}
            # r = lambda: random.randint(0, 255)
            # colors = {ot: '#{:02x}{:02x}{:02x}'.format(r(), r(), r()) for ot in object_types}

        for ot in object_types:
            self.add_item(item=ot, child=ObjectTypeEntryWidget(master=self,
                                                               ot=ot,
                                                               enabled=True,
                                                               count=counts[ot],
                                                               color=colors[ot]))


class ObjectTypeEntryWidget(DndListItem):
    def __init__(self, master, ot: str, enabled: bool, count: int, color: str, **kwargs):
        super().__init__(master=master, item=ot, draggable=False, **kwargs)

        # checkbox and name
        self.checkbox_var = tk.IntVar(value=int(enabled))
        self.checkbox = ttk.Checkbutton(master=self.interior,
                                        text=f"{ot} ({count})",
                                        command=self.update_ot_checkbox,
                                        variable=self.checkbox_var,
                                        bootstyle="round-toggle")
        self.checkbox.pack(side=LEFT)
        logger.info(str(ot) + " : " + str(color))
        tk.Label(master=self.interior, image=tk.PhotoImage(), autostyle=False,
                 width=10, height=10, bg=color).pack(side=RIGHT, padx=20)

    def update_ot_checkbox(self):
        ot_status = self.checkbox_var.get()
        item_status = 'on' if ot_status else 'off'
        logging.info(f"Object Type: {self.item} was toggled: {item_status}")

    def is_checked(self):
        return bool(self.checkbox_var.get())