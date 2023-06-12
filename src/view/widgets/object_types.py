import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import random

from view.components.dnd_list import DndList, DndListItem

logger = logging.getLogger("app_logger")

class ObjectTypeWidget(ttk.Frame):
    def __init__(self, master, object_types, counts, colors=None, **kwargs):
        super().__init__(master=master, **kwargs)

        self.list_widget = ObjectTypeListWidget(master=self, object_types=object_types, counts=counts, colors=None, on_swap=self.on_swap)
        self.list_widget.pack(side=TOP, fill=X)

        btn_frame = ttk.Frame(master=self)
        btn_frame.pack(side=TOP, fill=X, padx=20, pady=10)

        self.btn_apply = ttk.Button(master=btn_frame, text="Apply", bootstyle=PRIMARY, command=self.apply)
        self.btn_reset = ttk.Button(master=btn_frame, text="Reset", bootstyle=SECONDARY, command=self.reset)

        self.btn_reset.pack(side=RIGHT)
        self.btn_apply.pack(side=RIGHT, padx=10)

    def on_swap(self, order):
        logger.info(f"object types reordered: {order}")
        self.update_buttons()

    def on_check(self, list_item):
        logger.info(f"checkbox '{list_item.item}'")
        self.update_buttons()

    def update_buttons(self):
        if self.has_changes():
            self.btn_reset.pack(side=RIGHT)
            self.btn_apply.pack(side=RIGHT, padx=10)
        else:
            self.btn_reset.pack_forget()
            self.btn_apply.pack_forget()

    def has_changes(self):
        active_ots = [w.item for w in self.list_widget.items if w.is_checked()]

        # compare to model

        return True

    def apply(self):
        logger.debug("Apply")

    def reset(self):
        logger.debug("Reset")


class ObjectTypeListWidget(DndList):
    def __init__(self, master, object_types, counts, colors=None, on_swap=None, **kwargs):
        super().__init__(master, on_swap=on_swap, **kwargs)

        # TODO random color assignment, use nice color palette
        if colors is None:
            r = lambda: random.randint(0, 255)
            colors = {ot: '#{:02x}{:02x}{:02x}'.format(r(), r(), r()) for ot in object_types}

        for ot in object_types:
            self.add_item(item=ot, child=ObjectTypeEntryWidget(master=self,
                                                               ot=ot,
                                                               enabled=True,
                                                               count=counts[ot],
                                                               color=colors[ot],
                                                               on_change=master.on_check))


class ObjectTypeEntryWidget(DndListItem):
    def __init__(self, master, ot: str, enabled: bool, count: int, color: str, on_change: callable=None, **kwargs):
        super().__init__(master=master, item=ot, **kwargs)

        # checkbox and name
        self.checkbox_var = tk.IntVar(value=int(enabled))
        self.checkbox = ttk.Checkbutton(master=self.interior,
                                        text=f"{ot} ({count})",
                                        command=self.update_checkbox,
                                        variable=self.checkbox_var,
                                        bootstyle="round-toggle")
        self.checkbox.pack(side=LEFT)
        self.on_change = on_change
        # color display / color picker
        # color_border = ttk.Frame(master=self.interior, bg="black")
        # ot_bg_style = f"Colorbox:{ot}.TLabel"
        # ttk.style.Style.instance.configure(ot_bg_style, background=color, width=2, height=2)
        logger.info(str(ot) + " : " + str(color))
        tk.Label(master=self.interior, image=tk.PhotoImage(), autostyle=False,
                 width=10, height=10, bg=color).pack(side=RIGHT, padx=20)
        # color_border.pack(side=RIGHT, padx=10)
        # TODO color picker

    def update_checkbox(self, toggle=False):
        self.on_change(self)
        # if toggle:
        #     self.checkbox_var.set(1 - self.checkbox_var.get())
        # selected = bool(self.checkbox_var.get())
        # self.checkbox.config(bootstyle=PRIMARY if selected else SECONDARY)

    def is_checked(self):
        return bool(self.checkbox_var.get())