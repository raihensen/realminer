import logging
import tkinter as tk
from typing import List

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.filedialog as filedialog
from tkfontawesome import icon_to_image as fontawesome
from PIL import Image, ImageTk
import json
import os

from view.constants import *

logger = logging.getLogger("app_logger")


class WelcomeScreen:
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.window.title(WINDOW_TITLE)
        self.window.resizable(width=False, height=False)

        # background image
        # background_image = ImageTk.PhotoImage(Image.open("static/img/background/0-1(4).jpg"))
        # background_label = tk.Label(master=self.window, image=background_image)
        # background_label.place(x=0, y=0, relwidth=1, relheight=1)

        ICON_RECENT = fontawesome("history", fill="grey", scale_to_height=18)
        ICON_OPEN = fontawesome("folder-open", fill="white", scale_to_height=18)
        ICON_PLUS = fontawesome("plus", fill="white", scale_to_height=18)
        ICON_ARROW_RIGHT = fontawesome("arrow-right", fill="white", scale_to_height=18)

        style = ttk.Style()
        style.configure('title.TLabel', font=(None, 40))
        style.configure('large.primary.TButton', font=(None, 14))
        style.configure('large.secondary.TButton', font=(None, 14))
        style.configure('large.secondary.TMenubutton', font=(None, 14))

        # Title
        hero = tk.Frame(master=self.window)
        hero.pack(side=TOP, fill=X, expand=True)
        title_label = ttk.Label(master=hero, text=WINDOW_TITLE, bootstyle=DANGER, style="title.TLabel")
        title_label.pack(side=LEFT, fill=BOTH, padx=50, pady=50)

        main = tk.Frame(master=self.window, background="")
        main.pack(side=TOP, fill=BOTH, expand=True)
        row_recent = tk.Frame(master=main, background="")
        row_recent.pack(side=TOP, fill=X, pady=15)
        row_import = tk.Frame(master=main, background="")
        row_import.pack(side=TOP, fill=X, pady=15)

        recent_files = self.app.get_preference("recent_files")

        if recent_files:

            # ttk.Label(master=row_file, image=ICON_RECENT).pack(side=LEFT, padx=20)

            def set_selected_recent_file():
                file = self.var_recent_file.get()
                btn_recent.config(text=f"Recent file: {file}")

            btn_recent = ttk.Menubutton(master=row_recent, bootstyle=SECONDARY, style='large.secondary.TMenubutton')
            btn_recent.pack(side=LEFT, fill=X, expand=True, padx=10)

            menu_recent = ttk.Menu(btn_recent)
            self.var_recent_file = tk.StringVar(value=recent_files[0])

            for file in recent_files:
                menu_recent.add_radiobutton(label=file,
                                            value=file,
                                            variable=self.var_recent_file,
                                            command=set_selected_recent_file)
            btn_recent["menu"] = menu_recent
            set_selected_recent_file()

            btn_import = ttk.Button(master=row_recent, text="Import", image=ICON_ARROW_RIGHT, compound=LEFT,
                                    command=self.open_selected_recent_file,
                                    bootstyle=PRIMARY,
                                    style='large.primary.TButton')
            btn_import.pack(side=RIGHT, padx=10)

        btn_open = ttk.Button(master=row_import, text="Open new event log", image=ICON_OPEN, compound=LEFT,
                              command=self.open_file_dialog,
                              bootstyle=SECONDARY if recent_files else PRIMARY,
                              style='large.secondary.TButton' if recent_files else 'large.primary.TButton')
        btn_open.pack(side=LEFT, padx=10)

        # Checkbox for disabling demo popups
        self.checkbox_demo_popups_var = tk.IntVar(value=int(self.app.get_preference("show_demo_popups")))
        checkbox_demo_popups = ttk.Checkbutton(master=row_import,
                                               text=f"Show instructions",
                                               command=self.update_demo_popups_checkbox,
                                               variable=self.checkbox_demo_popups_var,
                                               bootstyle="round-toggle")
        checkbox_demo_popups.pack(side=LEFT, padx=10)

    def update_demo_popups_checkbox(self):
        state = bool(self.checkbox_demo_popups_var.get())
        self.app.set_preference("show_demo_popups", state)

    def open_selected_recent_file(self):
        self.open_file(self.var_recent_file.get())

    def open_file_dialog(self):
        recent_files = self.app.get_preference("recent_files")
        file = filedialog.askopenfile(filetypes=[("Object-centric event logs", ".csv .jsonocel")],
                                      initialdir="../data/datasets",
                                      initialfile=recent_files[0] if recent_files else None)
        if file is not None:
            self.open_file(file.name)

    def open_file(self, file):
        recent_files = [file] + [f for f in self.app.get_preference("recent_files") if f != file]
        self.app.set_preference("recent_files", recent_files)
        self.app.initialize(file)
