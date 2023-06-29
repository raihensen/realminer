import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkfontawesome import icon_to_image as fontawesome
import tkinter.dnd as tkdnd

import numpy as np


class DndList(tk.Frame):
    drag_handle_icon = None

    def __init__(self, master, accept_swap=None, on_swap=None, **kwargs):
        super().__init__(master=master, **kwargs)
        if DndList.drag_handle_icon is None:
            DndList.drag_handle_icon = fontawesome("grip-lines", fill="grey", scale_to_height=15)

        self._children = []
        # self.preview_line = tk.Label(master=self, image=tk.PhotoImage(), bg="grey")
        self.preview_line = ttk.Separator(master=self)
        self.source_index = None
        self.target_index = None

        self.accept_swap = accept_swap
        self.on_swap = on_swap

    def add_item(self, item=None, child=None) -> tk.Frame:
        if item is None:
            item = len(self._children)
        if child is None:
            child = DndListItem(master=self, item=item)

        child.item = item
        self._children.append(child)

        child.pack(side=TOP, fill=X)
        return child.interior

    @property
    def items(self):
        return self._children

    def dnd_accept(self, source, event):
        if isinstance(source, DndListItem):
            if source in self._children:
                self.source_index = self._children.index(source)
                return self
        return None

    def dnd_enter(self, source, event):
        pass

    def dnd_leave(self, source, event):
        pass

    def dnd_motion(self, child, event):
        bounds = [w.winfo_y() for w in self._children]
        bounds.append(self._children[-1].winfo_y() + self._children[-1].winfo_height())
        centers = [(bounds[i] + bounds[i + 1]) // 2 for i in range(len(bounds) - 1)]
        y = child.get_parent_coords(event, start_offset=False)[1]

        target_index = min((i for i, c in enumerate(centers) if y < c), default=len(centers))

        if self.target_index is None or self.target_index != target_index:
            if target_index == self.source_index + 1:
                # "to be placed after itself" -> don't move
                target_index = self.source_index
            # draw line
            self.target_index = target_index
            self.repaint_children()

    def dnd_commit(self, source, event=None):
        # Dropped
        s, t = self.source_index, self.target_index
        if t - s not in [0, 1]:
            # print(f"commit {s} -> {t}")

            before = [c for c in self._children[:t] if c is not source]
            after = [c for c in self._children[t:] if c is not source]
            new_order = before + [source] + after
            success = True
            if self.accept_swap is not None and callable(self.accept_swap):
                response = self.accept_swap([c.item for c in new_order])
                if response is False:
                    success = False
            if success:
                self._children = new_order
                if self.on_swap is not None and callable(self.on_swap):
                    self.on_swap([c.item for c in new_order])

        self.source_index = None
        self.target_index = None
        self.repaint_children()

    def dnd_end(self, event=None):
        if self.target_index is not None and self.source_index is not None:
            self.dnd_commit(self._children[self.source_index])

    def repaint_children(self):
        s, t = self.source_index, self.target_index
        preview_index = t
        if s == 0 and t == 0:
            preview_index = 1

        self.preview_line.pack_forget()
        for c in self._children:
            c.pack_forget()
        if preview_index is not None:
            for c in self._children[:preview_index]:
                c.pack(side=TOP, fill=X)
            self.preview_line.pack(side=TOP, fill=X, padx=10)
            for c in self._children[preview_index:]:
                c.pack(side=TOP, fill=X)
        else:
            for c in self._children:
                c.pack(side=TOP, fill=X)


class DndListItem(tk.Frame):
    def __init__(self, master: DndList, item, draggable=True, **kwargs):
        super().__init__(master=master, **kwargs)
        self.item = item

        if draggable:
            self.handle = tk.Label(master=self, image=DndList.drag_handle_icon, cursor="fleur")
            self.handle.bind("<Button-1>", self.dnd_start)
            self.handle.pack(side=LEFT, padx=5)

        self.interior = tk.Frame(master=self)
        self.interior.pack(side=LEFT, fill=X, padx=2, pady=2, expand=True)

        self.drag_offset = None

    def dnd_start(self, event):
        if tkdnd.dnd_start(self, event):
            self.drag_offset = np.array([event.x, event.y])

    def get_parent_coords(self, event, start_offset=True):
        p = np.array([self.master.winfo_rootx(), self.master.winfo_rooty()])
        m = np.array([event.x_root, event.y_root])
        if start_offset:
            return m - p - self.drag_offset
        return m - p

    def dnd_end(self, target, event):
        self.master.dnd_end(event)


class DndListTextItem(DndListItem):
    def __init__(self, master: DndList, text: str, item=None, **kwargs):
        super().__init__(master=master, item=item, **kwargs)
        tk.Label(master=self.interior, text=text).pack(side=LEFT)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("400x400")
    dnd_list = DndList(master=root)
    dnd_list.pack(fill=X)

    for text in "Hallo wie gehts dir".split():
        dnd_list.add_item(child=DndListTextItem(master=dnd_list, text=text))

    root.mainloop()
