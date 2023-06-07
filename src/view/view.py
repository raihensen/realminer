
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# from view.components.scrollable_frame import VerticalScrolledFrame
from view.components.accordion import Accordion
from view.widgets.object_types import ObjectTypeWidget
# from controller.controller import *

WINDOW_TITLE = "Object-centric Business App"
MAXIMIZED = True
SIDEBAR_WIDTH_RATIO = 0.2
SIDEBAR_MIN_WIDTH = 150
TOOLBAR_HEIGHT = 40


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        if MAXIMIZED:
            self.state('zoomed')


class View:
    def __init__(self, controller, theme):
        self.controller = controller
        self.window = Window()

        self.theme = theme

        self.window.rowconfigure(0, minsize=TOOLBAR_HEIGHT)
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, minsize=SIDEBAR_MIN_WIDTH, weight=1)
        self.window.columnconfigure(1, minsize=SIDEBAR_MIN_WIDTH/SIDEBAR_WIDTH_RATIO, weight=int(round(1 / SIDEBAR_WIDTH_RATIO, 0)) - 1)

        # Basic layout
        style = ttk.Style(theme)
        self.toolbar = ttk.Frame(master=self.window, bootstyle=DARK)
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        style.configure("sidebar.TFrame", background="#e0e0e0")
        # self.sidebar = VerticalScrolledFrame(master=self.window, style="sidebar.TFrame")
        self.sidebar = ScrolledFrame(master=self.window)
        self.sidebar.grid(row=1, column=0, sticky=NSEW)
        self.main = tk.Frame(master=self.window)
        self.main.grid(row=1, column=1, sticky=NSEW)

        # Create test button to demonstrate MVC event propagation
        self.test_label = tk.Label(master=self.main, text="---")
        self.test_btn = tk.Button(master=self.main, text="MVC Test", command=self.controller.test_action)
        self.test_label.pack()
        self.test_btn.pack()

        # Toolbar contents
        ttk.Label(master=self.toolbar, text="[Toolbar]", bootstyle=DARK).pack(side=LEFT)

        # Theme selection
        theme_menubutton = ttk.Menubutton(master=self.toolbar, text="Change theme", bootstyle=DARK)
        theme_menubutton.pack(side=RIGHT, padx=10, pady=10, fill=Y)
        theme_menu = ttk.Menu(theme_menubutton)
        theme_var = tk.StringVar(value=self.theme)
        for theme in ttk.style.STANDARD_THEMES:
            theme_menu.add_radiobutton(label=theme,
                                       variable=theme_var,
                                       command=lambda t=theme: self.change_theme(t))
        theme_menubutton["menu"] = theme_menu

        # Sidebar contents
        acc = Accordion(self.sidebar, title_height=50, bootstyle=SECONDARY)
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

    def change_theme(self, theme):
        print(f"Change to theme '{theme}'")
        self.style.theme_use(theme)

    def test_set_label(self, x):
        self.test_label.config(text=str(x))

    @property
    def style(self):
        return ttk.style.Style.instance

    def start(self):
        self.window.mainloop()

