'''The Accordion widget inherits from Tkinter's Frame class and provides stacked
expandable and collapseable containers for displaying other widgets.

Compliant with Python 2.5-2.7

Author: @ifthisthenbreak
'''

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkfontawesome import icon_to_image as fontawesome

DEFAULT_STYLE = {
    'title_bg': 'ghost white',
    'title_fg': 'black',
    'highlight': 'white smoke',
    'font_size': 12
}

icons = {}


def get_icon(name, fill=None, bootstyle=None, height=15):
    if bootstyle is not None and fill is None:
        fill = "red"
    key = f"{name}-{fill}-{height}"
    if key not in icons:
        icons[key] = fontawesome(name, fill=fill, scale_to_height=height)
    return icons[key]


class Chord(tk.Frame):
    def __init__(self, wrapper, accordion, title='', expanded=False, bootstyle=None, *args, **kw):
        ttk.Frame.__init__(self, master=wrapper, *args, **kw)
        self.accordion = accordion
        self.title = title
        self.expanded = expanded
        self.icon = None

        self.title_button = ttk.Button(wrapper,
                                       bootstyle=bootstyle,
                                       image=self.accordion.icon_expanded if self.expanded else self.accordion.icon_collapsed,
                                       text=self.title,
                                       compound=LEFT)
        self.title_button.bind('<Button-1>', lambda e: self._click_handler())
        self.title_button.pack(side=TOP, fill=X, expand=True)
        # c.icon = ttk.Button(title,
        #                     width=20,
        #                     bootstyle=self.bootstyle,
        #                     # bg=self.style['title_bg'],
        #                     image=self.icon_expanded if c.expanded else self.icon_collapsed)
        # label = ttk.Button(title, bootstyle=self.bootstyle, text=c.title)

        # c.icon.pack(side=LEFT)
        # label.pack(side=LEFT)

    def _click_handler(self):
        print(self.title)
        if not self.expanded:
            self.expanded = True
            self.title_button.config(image=self.accordion.icon_expanded)
            self.pack(side=TOP, fill=X, expand=True)
        else:
            self.expanded = False
            self.title_button.config(image=self.accordion.icon_collapsed)
            self.pack_forget()


class Accordion(ttk.Frame):
    def __init__(self, parent, bootstyle=None, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.bootstyle = bootstyle
        self.style = {k: kwargs.get(k, default) for k, default in DEFAULT_STYLE.items()}
        self.columnconfigure(0, weight=1)

        # TODO get bootstyle text color
        fg = ttk.Style.instance.colors.selectfg
        self.icon_expanded = get_icon("caret-down", fg, self.style['font_size'])
        self.icon_collapsed = get_icon("caret-right", fg, self.style['font_size'])

    def add_chord(self, title='', expanded=False, **kwargs) -> Chord:
        self.update_idletasks()
        # row = 0
        # width = max([c.winfo_reqwidth() for c in chords])

        wrapper = tk.Frame(self)
        c = Chord(wrapper, self, title, expanded, bootstyle=self.bootstyle, **kwargs)
        if c.expanded:
            c.pack(side=TOP, fill=X, expand=True)
        wrapper.pack(side=TOP, fill=X)
        return c


if __name__ == '__main__':
    from tkinter import Entry, Button, Text

    root = tk.Tk()

    # create the Accordion
    acc = Accordion(root)

    # first chord
    first_chord = Chord(acc, title='First Chord', bg='white')
    tk.Label(first_chord, text='hello world', bg='white').pack()

    # second chord
    second_chord = Chord(acc, title='Second Chord', bg='white')
    Entry(second_chord).pack()
    Button(second_chord, text='Button').pack()

    # third chord
    third_chord = Chord(acc, title='Third Chord', bg='white')
    Text(third_chord).pack()

    # append list of chords to Accordion instance
    acc.append_chords([first_chord, second_chord, third_chord])
    acc.pack(fill=BOTH, expand=1)

    root.mainloop()
