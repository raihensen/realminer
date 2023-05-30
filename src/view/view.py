
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *

from src.view.components.scrollable_frame import VerticalScrolledFrame
from src.view.components.accordion import Accordion
from src.view.widgets.object_types import ObjectTypeWidget
# from src.controller.controller import *

WINDOW_TITLE = "Object-centric Business App"
MAXIMIZED = True
SIDEBAR_WIDTH_RATIO = 0.2
SIDEBAR_MIN_WIDTH = 200
TOOLBAR_HEIGHT = 40


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        if MAXIMIZED:
            self.state('zoomed')


class View:
    def __init__(self, controller):
        self.controller = controller
        self.window = Window()

        self.window.rowconfigure(0, minsize=TOOLBAR_HEIGHT)
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, minsize=SIDEBAR_MIN_WIDTH, weight=1)
        self.window.columnconfigure(1, minsize=SIDEBAR_MIN_WIDTH, weight=int(round(1 / SIDEBAR_WIDTH_RATIO, 0)) - 1)

        # Basic layout
        style = ttk.Style()
        self.toolbar = tk.Frame(master=self.window, bg="#303030")
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        style.configure("sidebar.TFrame", background="#e0e0e0")
        self.sidebar = VerticalScrolledFrame(master=self.window, style="sidebar.TFrame")
        self.sidebar.grid(row=1, column=0, sticky=NSEW)
        self.main = tk.Frame(master=self.window, bg="#ffffff")
        self.main.grid(row=1, column=1, sticky=NSEW)

        # Create test button to demonstrate MVC event propagation
        self.test_label = tk.Label(master=self.main, text="---")
        self.test_btn = tk.Button(master=self.main, text="MVC Test", command=self.controller.test_action)
        self.test_label.pack()
        self.test_btn.pack()

        # Toolbar contents
        tk.Label(master=self.toolbar, text="[Toolbar]", bg="#303030", fg="#a0a0a0").pack(side=LEFT)

        # Sidebar contents
        acc = Accordion(self.sidebar.interior, title_height=50)
        # Object types
        self.ot_container = acc.add_chord(title='Object types', expanded=True)
        self.ot_widget = None
        # Activities
        self.act_container = acc.add_chord(title='Activities')
        self.act_widget = None
        tk.Label(self.act_container, text='hello world', bg='white').pack()

        acc.pack(side=TOP, fill=X)

    def init_object_types(self, object_types, counts, colors=None):
        self.ot_widget = ObjectTypeWidget(self.ot_container, object_types, counts, colors)
        self.ot_widget.pack(fill=X)

    def init_activities(self, activities):
        pass

    def test_set_label(self, x):
        self.test_label.config(text=str(x))

    def start(self):
        self.window.mainloop()


if __name__ == "__main__":
    View().start()


