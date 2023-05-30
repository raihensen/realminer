
import tkinter as tk
from tkinter.constants import *


BUTTON_PRIMARY = "primary"
BUTTON_


class Button(tk.Button):
    def __init__(self, master, style=None, **kwargs):
        style = kwargs.pop("style")
        super().__init__(master=master, **kwargs)