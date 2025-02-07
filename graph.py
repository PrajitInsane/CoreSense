import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

class Graph:
    def __init__(self):
        self.fig = Figure(figsize=(5, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("CPU Usage (%)")
        self.ax.set_ylim(0, 100)
        self.data = [0] * 20  # Keep last 20 readings
        self.line, = self.ax.plot(self.data, 'r-')

        self.canvas = FigureCanvas(self.fig)

    def update_graph(self, cpu_usage):
        self.data.append(cpu_usage)
        self.data.pop(0)
        self.line.set_ydata(self.data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
