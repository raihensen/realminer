
from src.view.view import View


class Controller:
    view: View

    def __init__(self, model):
        self.model = model

    def init_view(self):
        self.view.init_object_types(object_types=self.model.ocel.object_types,
                                    counts=self.model.ocel.object_type_counts,
                                    colors=None)

    def test_action(self):
        self.view.test_set_label(self.model.ocel.object_types)
