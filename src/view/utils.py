

class ResizeTracker:
    """ Toplevel windows resize event tracker. """
    # https://stackoverflow.com/questions/61712329/tkinter-track-window-resize-specifically

    def __init__(self, window, app):
        self.window = window
        self.app = app
        self.width, self.height = window.winfo_width(), window.winfo_height()
        self.maximized = self.is_maximized()
        self._func_id = None

    def bind_config(self):
        self._func_id = self.window.bind("<Configure>", self.on_resize)

    def unbind_config(self):  # Untested.
        if self._func_id:
            self.window.unbind("<Configure>", self._func_id)
            self._func_id = None

    def on_resize(self, event):
        if event.widget != self.window:
            return
        maximized = self.is_maximized()
        if self.width == event.width and self.height == event.height and self.maximized == maximized:
            return

        if maximized != self.maximized:
            self.app.set_preference("maximized", maximized)
        # print(f'Resize window: {event.width}x{event.height}, {"maximized" if maximized else "not maximized"}\n')
        self.width, self.height, self.maximized = event.width, event.height, maximized

    def is_maximized(self):
        return self.window.state() == "zoomed"