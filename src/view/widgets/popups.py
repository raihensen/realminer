import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification

my_w = ttk.Window(themename="lumen")
my_w.geometry("300x200")  # width and height

class Toast(ToastNotification):
    def __init__(self,title, message, position, bootstyle, icon):
        super().__init__(title=title, message=message, position=position, bootstyle=bootstyle, icon=icon)
        self.enabled = True