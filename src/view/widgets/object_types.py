import tkinter as tk
from tkinter.constants import *
# import tkinter.dnd as tkdnd
# from tkfontawesome import icon_to_image as fontawesome
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
                                                               count=counts[ot],
                                                               color=colors[ot]))

    def on_swap(self, order):
        print(f"object types reordered: {order}")
        return True


class ObjectTypeEntryWidget(DndListItem):
    def __init__(self, master, ot, count, color, **kwargs):
        super().__init__(master=master, item=ot, **kwargs)

        # checkbox
        self.checkbox_var = tk.IntVar()
        self.checkbox = tk.Checkbutton(master=self.interior, command=self.update_checkbox, variable=self.checkbox_var)
        self.checkbox.select()
        self.checkbox.pack(side=LEFT)

        # name
        self.label = tk.Label(master=self.interior, text=f"{ot} ({count})")
        self.label.bind("<Button-1>", lambda e: self.update_checkbox(toggle=True))
        self.label.pack(side=LEFT)

        # color display / color picker
        color_border = tk.LabelFrame(master=self.interior, bg="black")
        img = tk.PhotoImage()
        tk.Label(master=color_border, image=img, width=10, height=10, bg=color).pack()
        color_border.pack(side=RIGHT, padx=10)
        # TODO color picker

    def update_checkbox(self, toggle=False):
        if toggle:
            self.checkbox.toggle()
        selected = bool(self.checkbox_var.get())
        self.label.config(fg="black" if selected else "grey")

