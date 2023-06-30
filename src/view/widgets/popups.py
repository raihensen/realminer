import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification

class Toast(ToastNotification):
    def __init__(self,title, message, position, bootstyle, icon):
        super().__init__(title=title, message=message, position=position, bootstyle=bootstyle, icon=icon)
        self.enabled = True