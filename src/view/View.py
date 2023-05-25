
import tkinter as tk

WINDOW_TITLE = "Object-centric Business App"
MAXIMIZED = True


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        if MAXIMIZED:
            self.state('zoomed')


class View:
    def __init__(self):
        self.window = Window()
        self.window.mainloop()


if __name__ == "__main__":
    View()

