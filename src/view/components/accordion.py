'''The Accordion widget inherits from Tkinter's Frame class and provides stacked
expandable and collapseable containers for displaying other widgets.

Compliant with Python 2.5-2.7

Author: @ifthisthenbreak
'''

import tkinter as tk
from tkfontawesome import icon_to_image as fontawesome

DEFAULT_STYLE = {
    'title_bg': 'ghost white',
    'title_fg': 'black',
    'highlight': 'white smoke',
    'font_size': 12
}

icons = {}


def get_icon(name, fill="black", height=15):
    key = f"{name}-{fill}-{height}"
    if key not in icons:
        icons[key] = fontawesome(name, fill=fill, scale_to_height=height)
    return icons[key]


class Chord(tk.Frame):
    '''Tkinter Frame with title argument'''

    def __init__(self, parent, title='', expanded=False, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.title = title
        self.expanded = expanded
        self.icon = None


class Accordion(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent)
        self.style = {k: kwargs.get(k, default) for k, default in DEFAULT_STYLE.items()}
        self.columnconfigure(0, weight=1)

        self.icon_expanded = get_icon("caret-down", self.style['title_fg'], self.style['font_size'])
        self.icon_collapsed = get_icon("caret-right", self.style['title_fg'], self.style['font_size'])

        # self.wrappers = [Frame(self) for _ in range(n)]
        # self.chords = [Chord()]

    # def append_chords(self, chords=[]):
    #     '''pass a [list] of Chords to the Accordion object'''

    def add_chord(self, title='', expanded=False, **kwargs) -> Chord:
        self.update_idletasks()
        # row = 0
        # width = max([c.winfo_reqwidth() for c in chords])

        wrapper = tk.Frame(self)
        c = Chord(wrapper, title, expanded, **kwargs)

        # for c, wrapper in zip(chords, wrappers):
        title = tk.Frame(wrapper,
                      # compound='center',
                      # width=width,
                      height=self.style.get("title_height", None),
                      bg=self.style['title_bg'],
                      bd=2)
        c.icon = tk.Label(title, width=20,
                       bg=self.style['title_bg'],
                       image=self.icon_expanded if c.expanded else self.icon_collapsed)
        label = tk.Label(title, text=c.title,
                      bg=self.style['title_bg'],
                      fg=self.style['title_fg'])

        c.icon.pack(side=tk.LEFT)
        label.pack(side=tk.LEFT)

        title.pack(side=tk.TOP, fill=tk.X, expand=True)
        if c.expanded:
            c.pack(side=tk.TOP, fill=tk.X, expand=True)
        wrapper.pack(side=tk.TOP, fill=tk.X)

        # title.grid(row=row, column=0, sticky="EW")
        # c.grid(row=row + 1, column=0, sticky='EW')
        # if not c.expanded:
        #     c.grid_remove()
        # row += 2

        widgets = [title, label, c.icon]
        for w in widgets:
            w.bind('<Button-1>', lambda e, c=c: self._click_handler(c))
        title.bind('<Enter>', lambda e, widgets=widgets: [w.config(bg=self.style['highlight']) for w in widgets])
        title.bind('<Leave>', lambda e, widgets=widgets: [w.config(bg=self.style['title_bg']) for w in widgets])

        return c

    def _click_handler(self, chord):
        # if len(chord.grid_info()) == 0:
        if not chord.expanded:
            chord.expanded = True
            chord.icon.config(image=self.icon_expanded)
            chord.icon.image = self.icon_expanded
            # chord.grid()
            chord.pack(side=tk.TOP, fill=tk.X, expand=True)
        else:
            chord.expanded = False
            chord.icon.config(image=self.icon_collapsed)
            chord.icon.image = self.icon_collapsed
            # chord.grid_remove()
            chord.pack_forget()


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
    acc.pack(fill='both', expand=1)

    root.mainloop()
