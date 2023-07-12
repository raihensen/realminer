import tkinter as tk
import math

SPINNER_DELAY = 20
SPINNER_ANGLE_STEP = 7.5
WIDTH = 200
HEIGHT = 200
TEXT_HEIGHT = 50
RADIUS = 20
CIRCLE_RADIUS = 3


class Spinner(tk.Canvas):
    def __init__(self, master: tk.Tk, text: str = None, width=WIDTH, height=HEIGHT):

        self.width = width
        self.height = height
        self.text = text
        self.stopped = False

        # Create a Canvas widget
        self.canvas_height = self.height + (0 if text is None else TEXT_HEIGHT)
        super().__init__(master, width=self.width, height=self.canvas_height)
        self.configure(bg="white")

        # Start the spinner animation
        self.animate_spinner(angle=0)

    def fill(self):
        self.master.geometry(f"{self.width}x{self.canvas_height}")
        return self.pack()

    def overlay(self):
        return self.place(x=self.master.winfo_width() / 2 - self.width / 2,
                          y=self.master.winfo_height() / 2 - self.height / 2)

    def set_text(self, text: str = None):
        if (text is None) != (self.text is None):
            self.canvas_height = self.height + (0 if text is None else TEXT_HEIGHT)
            self.config(height=self.canvas_height)
        self.text = text

    def stop(self):
        self.stopped = True

    def animate_spinner(self, angle):
        if self.stopped:
            return
        # Clear the canvas
        self.delete("all")
        # Write text
        if self.text is not None:
            self.create_text(self.width / 2, self.height + TEXT_HEIGHT / 2, text=self.text)

        num_circles = 12
        x, y = self.width / 2, self.height / 2

        # Calculate the angle between each small circle
        angle_increment = 360 / num_circles

        for i in range(num_circles):
            # Calculate the position of each small circle
            circle_x = x + RADIUS * math.cos(math.radians(angle + angle_increment * i))
            circle_y = y + RADIUS * math.sin(math.radians(angle + angle_increment * i))

            # Calculate the opacity based on the circle index
            a = int(.1 * num_circles)
            opacity = max(.0, (i - a) / (num_circles - a))
            color = "#" + 3 * hex(int((1 - opacity) * 255))[2:]

            # Draw each small circle with varying opacity
            self.create_oval(circle_x - CIRCLE_RADIUS,
                             circle_y - CIRCLE_RADIUS,
                             circle_x + CIRCLE_RADIUS,
                             circle_y + CIRCLE_RADIUS,
                             fill=color, outline="", tags="spinner")

        # Update the angle for the next frame
        angle += SPINNER_ANGLE_STEP

        # Schedule the next animation frame
        self.after(SPINNER_DELAY, self.animate_spinner, angle)


if __name__ == '__main__':
    root = tk.Tk()
    Spinner(master=root).pack()
    root.mainloop()
