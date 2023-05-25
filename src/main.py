
from view.view import View
from model.model import *
from controller.controller import *

# Startup code of our app, initializing the main classes


class App:
    def __init__(self):
        self.model = Model()
        self.controller = Controller(self.model)
        self.view = View(self.controller)
        self.controller.view = self.view


app = App()
app.view.start()
