
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import random

from src.view.components.dnd_list import DndList, DndListItem

# DRAG_HANDLE_ICON = None


class ObjectTypeWidget(DndList):
    def __init__(self, master, object_types, counts, colors=None, **kwargs):
        super().__init__(master, on_swap=self.on_swap, **kwargs)

        # TODO random color assignment, use nice color palette
        if colors is None:
            r = lambda: random.randint(0, 255)
            colors = {ot: '#{:02x}{:02x}{:02x}'.format(r(), r(), r()) for ot in object_types}

        for ot in object_types:
            self.add_item(item=ot, child=ObjectTypeEntryWidget(master=self,
                                                               ot=ot,
                                                               enabled=True,
                                                               count=counts[ot],
                                                               color=colors[ot]))

    def on_swap(self, order):
        print(f"object types reordered: {order}")
        return True


class ObjectTypeEntryWidget(DndListItem):
    def __init__(self, master, ot: str, enabled: bool, count: int, color: str, **kwargs):
        super().__init__(master=master, item=ot, **kwargs)

        # checkbox and name
        self.checkbox_var = tk.IntVar(value=int(enabled))
        self.checkbox = ttk.Checkbutton(master=self.interior,
                                        text=f"{ot} ({count})",
                                        command=self.update_checkbox,
                                        variable=self.checkbox_var,
                                        bootstyle="round-toggle")
        self.checkbox.pack(side=LEFT)

        # color display / color picker
        # color_border = ttk.Frame(master=self.interior, bg="black")
        # ot_bg_style = f"Colorbox:{ot}.TLabel"
        # ttk.style.Style.instance.configure(ot_bg_style, background=color, width=2, height=2)
        print(ot, color)
        tk.Label(master=self.interior, image=tk.PhotoImage(), autostyle=False,
                 width=10, height=10, bg=color).pack(side=RIGHT, padx=20)
        # color_border.pack(side=RIGHT, padx=10)
        # TODO color picker

    def update_checkbox(self, toggle=False):
        if toggle:
            self.checkbox_var.set(1 - self.checkbox_var.get())
        selected = bool(self.checkbox_var.get())
        # self.label.config()
        # self.label.config(fg="black" if selected else "grey")

