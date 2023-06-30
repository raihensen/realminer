import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification


class Toast(ToastNotification):
    window: tk.Tk = None
    toasts = []

    def __init__(self, title, message, position=None, bootstyle=None, icon=None):
        for toast in Toast.toasts:
            toast.hide_toast()
        Toast.toasts.append(self)

        if position is None and Toast.window is not None:
            expected_size = (200, 100)
            x = int(Toast.window.winfo_x() + .5 * Toast.window.winfo_width() - .5 * expected_size[0])
            y = int(Toast.window.winfo_y() + .5 * Toast.window.winfo_height() - .5 * expected_size[1])
            position = (x, y, 'ne')

        icon='\u26CF'
        super().__init__(title=title, message=message, position=position, bootstyle=bootstyle, icon=icon)
        self.enabled = True
