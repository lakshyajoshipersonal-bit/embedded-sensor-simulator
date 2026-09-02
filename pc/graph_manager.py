from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GraphManager:
    def __init__(self):
        self.figure = Figure()
        self.figure.patch.set_facecolor("#1e1e1e")
        self.canvas = FigureCanvas(self.figure)

        self.canvas.setMinimumHeight(480)

        self.ax = self.figure.add_subplot(3,1,1)
        self.ax1 = self.figure.add_subplot(3,1,2)
        self.ax2 = self.figure.add_subplot(3,1,3)

        self.temperature_history = []
        self.time_history = []
        self.light_history = []
        self.humidity_history = []

        self.temperature_threshold = 30
        self.light_threshold = 300

        self.setup_graphs()

    def setup_graphs(self):
        self.ax.clear()
        self.ax1.clear()
        self.ax2.clear()

        self.ax.set_title("Temperature Over Time")
        self.ax.set_ylabel("Temperature (°C)")

        self.ax1.set_title("Light Level Over Time")
        self.ax1.set_ylabel("Light Level")

        self.ax2.set_title("Humidity Over Time")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Humidity Level (%)")

        self.style_axes()

        self.figure.tight_layout()
        self.canvas.draw()

    def add_reading(self, current_time, temperature, light, humidity):
        self.time_history.append(current_time)
        self.temperature_history.append(temperature)
        self.light_history.append(light)
        self.humidity_history.append(humidity)

        while self.time_history and current_time - self.time_history[0] > 30:
            self.time_history.pop(0)
            self.temperature_history.pop(0)
            self.light_history.pop(0)
            self.humidity_history.pop(0)

        self.draw_graphs()
        

    def draw_graphs(self):
        self.ax.clear()
        self.ax1.clear()
        self.ax2.clear()

        self.ax.plot(self.time_history, self.temperature_history)
        self.ax.axhline(y = self.temperature_threshold, linestyle="--", label="High Temp Threshold")
        self.ax.set_title("Temperature Over Time")
        self.ax.set_ylabel("Temperature (°C)")

        legend = self.ax.legend()
        if legend is not None:
            legend.get_frame().set_facecolor("#2b2b2b")
            legend.get_frame().set_edgecolor("white")

            for text in legend.get_texts():
                text.set_color("white")
        
        self.ax1.plot(self.time_history, self.light_history)
        self.ax1.axhline(y = self.light_threshold, linestyle="--", label="Dark Threshold")
        self.ax1.set_title("Light Level Over Time")
        self.ax1.set_ylabel("Light Level")

        legend = self.ax1.legend()
        if legend is not None:
            legend.get_frame().set_facecolor("#2b2b2b")
            legend.get_frame().set_edgecolor("white")
        
            for text in legend.get_texts():
                text.set_color("white")

        self.ax2.plot(self.time_history, self.humidity_history)
        self.ax2.set_title("Humidity Over Time")
        self.ax2.set_xlabel("Time(s)")
        self.ax2.set_ylabel("Humidity (%)")

        self.style_axes()

        self.figure.tight_layout()
        self.canvas.draw()

    def reset(self):
        self.time_history.clear()
        self.temperature_history.clear()
        self.light_history.clear()
        self.humidity_history.clear()

        self.setup_graphs()

    def style_axes(self):
        for axis in [self.ax, self.ax1, self.ax2]:
            axis.set_facecolor("#1e1e1e")

            axis.tick_params(axis="both",colors="white")

            axis.xaxis.label.set_color("white")
            axis.yaxis.label.set_color("white")
            axis.title.set_color("white")

            for spine in axis.spines.values():
                spine.set_color("white")

    def set_thresholds(self, temp_threshold, light_threshold):
        self.temperature_threshold = temp_threshold
        self.light_threshold = light_threshold
        self.draw_graphs()

