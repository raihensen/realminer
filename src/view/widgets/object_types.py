
import tkinter as tk
import random


class ObjectTypeWidget(tk.Frame):
    def __init__(self, master, object_types, counts, colors=None, **kwargs):
        super().__init__(master, **kwargs)

        # TODO random color assignment, use nice color palette
        if colors is None:
            r = lambda: random.randint(0, 255)
            colors = {ot: '#{:02x}{:02x}{:02x}'.format(r(), r(), r()) for ot in object_types}

        entries = [ObjectTypeEntryWidget(master=self, name=ot, count=counts[ot], color=colors[ot]) for ot in object_types]
        for w in entries:
            w.pack(side=tk.TOP, fill=tk.X)


class ObjectTypeEntryWidget(tk.Frame):
    def __init__(self, master, name, count, color, **kwargs):
        super().__init__(master, **kwargs)

        # drag handle
        # TODO

        # name
        tk.Label(master=self, text=f"{name} ({count})").pack(side=tk.LEFT)

        # color display / color picker
        color_border = tk.LabelFrame(master=self, bg="black", width=12, height=12, bd=1)
        img = tk.PhotoImage()
        tk.Label(master=color_border, image=img, width=10, height=10, bg=color).pack()
        color_border.pack(side=tk.RIGHT, padx=10)
        # TODO color picker


