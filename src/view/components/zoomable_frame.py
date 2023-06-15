# -*- coding: utf-8 -*-

# from https://stackoverflow.com/questions/41656176/tkinter-canvas-zoom-move-pan/48137257#48137257

# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large zooms.
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


class AutoScrollbar(ttk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')


class BoundingBox:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def contains(self, x, y) -> bool:
        return self.x0 < x < self.x1 and self.y0 < y < self.y1

    @staticmethod
    def intersect(a, b):
        return BoundingBox(max(a.x0, b.x0), max(a.y0, b.y0), min(a.x1, b.x1), min(a.y1, b.y1))

    @staticmethod
    def union(a, b):
        return BoundingBox(min(a.x0, b.x0), min(a.y0, b.y0), max(a.x1, b.x1), max(a.y1, b.y1))


class AdvancedZoom(ttk.Frame):
    ''' Advanced zoom of the image '''

    def __init__(self, master, path):
        ''' Initialize the main Frame '''
        ttk.Frame.__init__(self, master=master)

        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self, orient='vertical')
        hbar = AutoScrollbar(self, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>', self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>', self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>', self.wheel)  # only with Linux, wheel scroll up
        self.image = Image.open(path)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        # Plot some optional random rectangles for the test purposes
        # minsize, maxsize, number = 5, 20, 10
        # for n in range(number):
        #     x0 = random.randint(0, self.width - maxsize)
        #     y0 = random.randint(0, self.height - maxsize)
        #     x1 = x0 + random.randint(minsize, maxsize)
        #     y1 = y0 + random.randint(minsize, maxsize)
        #     color = ('red', 'orange', 'yellow', 'green', 'blue')[random.randint(0, 4)]
        #     self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, activefill='black')
        self.show_image()

    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = BoundingBox(*self.canvas.bbox(self.container))  # get image area
        if bbox.contains(x, y):
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = BoundingBox(*self.canvas.bbox(self.container))  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = BoundingBox(bbox1.x0 + 1, bbox1.y0 + 1, bbox1.x1 - 1, bbox1.y1 - 1)
        bbox2 = BoundingBox(self.canvas.canvasx(0),  # get visible area of the canvas
                            self.canvas.canvasy(0),
                            self.canvas.canvasx(self.canvas.winfo_width()),
                            self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = BoundingBox.union(bbox1, bbox2)  # get scroll region box
        if bbox.x0 == bbox2.x0 and bbox.x1 == bbox2.x1:  # whole image in the visible area
            bbox.x0 = bbox1.x0
            bbox.x1 = bbox1.x1
        if bbox.y0 == bbox2.y0 and bbox.y1 == bbox2.y1:  # whole image in the visible area
            bbox.y0 = bbox1.y0
            bbox.y1 = bbox1.y1

        canvas_size = BoundingBox(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height())
        scrollregion = BoundingBox.intersect(bbox, canvas_size)
        # scrollregion = bbox
        # print(f"bbox: {scrollregion}")
        #
        # self.canvas.configure(scrollregion=scrollregion)  # set scroll region

        x1 = max(bbox2.x0 - bbox1.x0, 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2.y0 - bbox1.y0, 0)
        x2 = min(bbox2.x1, bbox1.x1) - bbox1.x0
        y2 = min(bbox2.y1, bbox1.y1) - bbox1.y0
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it is in the visible area
            x = min(int(x2 / self.imscale), self.width)  # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2.x0, bbox1.x0), max(bbox2.y0, bbox1.y0),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection


if __name__ == '__main__':
    path = '../../static/img/ocpn.png'  # place path to your image here
    root = tk.Tk()
    root.title('Zoom with mouse wheel')
    app = AdvancedZoom(root, path=path)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
