import tkinter as tk
import tkinter.dnd as tkdnd
from tkfontawesome import icon_to_image as fontawesome
import random

DRAG_HANDLE_ICON = None


class ObjectTypeWidget(tk.Frame):
    def __init__(self, master, object_types, counts, colors=None, **kwargs):
        super().__init__(master, **kwargs)

        # TODO random color assignment, use nice color palette
        if colors is None:
            r = lambda: random.randint(0, 255)
            colors = {ot: '#{:02x}{:02x}{:02x}'.format(r(), r(), r()) for ot in object_types}

        self.entries = [ObjectTypeEntryWidget(master=self,
                                              name=ot,
                                              count=counts[ot],
                                              color=colors[ot]) for ot in object_types]
        for w in self.entries:
            w.pack(side=tk.TOP, fill=tk.X)


class ObjectTypeEntryWidget(tk.Frame):
    def __init__(self, master, name, count, color, **kwargs):
        global DRAG_HANDLE_ICON
        super().__init__(master, **kwargs)

        # drag handle
        # TODO
        if DRAG_HANDLE_ICON is None:
            DRAG_HANDLE_ICON = fontawesome("grip-lines", fill="grey", scale_to_height=15)
        drag_handle = tk.Label(master=self, image=DRAG_HANDLE_ICON, cursor="fleur")
        drag_handle.bind("<Button-1>", lambda e: tkdnd.dnd_start(self, e))
        drag_handle.pack(side=tk.LEFT, padx=5)

        # checkbox
        self.checkbox_var = tk.IntVar()
        self.checkbox = tk.Checkbutton(master=self, command=self.update_checkbox, variable=self.checkbox_var)
        self.checkbox.select()
        self.checkbox.pack(side=tk.LEFT)

        # name
        self.label = tk.Label(master=self, text=f"{name} ({count})")
        self.label.bind("<Button-1>", lambda e: self.update_checkbox(toggle=True))
        self.label.pack(side=tk.LEFT)

        # color display / color picker
        color_border = tk.LabelFrame(master=self, bg="black", width=12, height=12, bd=1)
        img = tk.PhotoImage()
        tk.Label(master=color_border, image=img, width=10, height=10, bg=color).pack()
        color_border.pack(side=tk.RIGHT, padx=10)
        # TODO color picker

    def dnd_end(self, target, event):
        print("end")

    def update_checkbox(self, toggle=False):
        if toggle:
            self.checkbox.toggle()
        selected = bool(self.checkbox_var.get())
        self.label.config(fg="black" if selected else "grey")

