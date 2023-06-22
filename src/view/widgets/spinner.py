import tkinter as tk
import math

SPINNER_DELAY = 20
SPINNER_ANGLE_STEP = 7.5
WIDTH = 200
HEIGHT = 200
RADIUS = 20
CIRCLE_RADIUS = 3


class Spinner(tk.Canvas):
    def __init__(self, master: tk.Tk):
        master.geometry(f"{WIDTH}x{HEIGHT}")

        # Create a Canvas widget
        super().__init__(master, width=WIDTH, height=HEIGHT, bg="white")

        # Start the spinner animation
        self.animate_spinner(angle=0)

    def animate_spinner(self, angle):
        # Clear the canvas
        self.delete("all")

        num_circles = 12
        x, y = WIDTH / 2, HEIGHT / 2

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
