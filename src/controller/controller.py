
from src.view.view import View


class Controller:
    view: View

    def __init__(self, model):
        self.model = model

    def test_action(self):
        self.view.test_set_label(self.model.random_number())

