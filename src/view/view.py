
import tkinter as tk
# from src.controller.controller import *

WINDOW_TITLE = "Object-centric Business App"
MAXIMIZED = True


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

        # Create test button to demonstrate MVC event propagation
        self.test_label = tk.Label(master=self.window, text="---")
        self.test_btn = tk.Button(master=self.window, text="MVC Test", command=self.controller.test_action)
        self.test_label.pack()
        self.test_btn.pack()

    def test_set_label(self, x):
        self.test_label.config(text=str(x))

    def start(self):
        self.window.mainloop()


if __name__ == "__main__":
    View().start()


