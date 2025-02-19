import gi
import platform
import re
import psutil
import subprocess
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from system_info import get_system_info
from sensors import (
    get_temp1, get_temp2, get_temp3, get_temp4, get_temp5, get_temp6, 
    get_core0, get_core1, get_core2, get_core3, get_fan_speed
)
from disk_usage import create_disk_graph
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class SensorApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="CoreSense")
        self.set_default_size(700, 700)
        self.set_border_width(20)

        # Main Grid Layout
        grid = Gtk.Grid()
        grid.set_row_spacing(15)
        grid.set_column_spacing(20)
        self.add(grid)
        # Create HeaderBar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title("CoreSense")

        # Create About Button
        about_button = Gtk.Button(label="About")
        about_button.connect("clicked", self.show_about_dialog)
        header_bar.pack_end(about_button)  # Adds to the right side

        # Set the header bar as the window title bar
        self.set_titlebar(header_bar)

        # System Information
        system_info = get_system_info()
        self.system_info_label = Gtk.Label()
        self.system_info_label.set_margin_end(10)
        self.system_info_label.set_markup(system_info)
        self.system_info_label.set_halign(Gtk.Align.CENTER)
        frame_sys_info = Gtk.Frame(label="System Information")
        frame_sys_info.set_label_align(0.5, 0.5)
        frame_sys_info.add(self.system_info_label)
        grid.attach(frame_sys_info, 0, 0, 1, 2)
        

        # Create a frame for CPU temperature section
        frame_cpu_temp = Gtk.Frame(label="CPU Temperature")
        frame_cpu_temp.set_label_align(0.5,0.5)
        frame_cpu_temp.set_margin_bottom(10)
        frame_cpu_temp.set_margin_start(10)
        frame_cpu_temp.set_margin_end(10)

        # Create a vertical box to contain both label and graph
        vbox_cpu_temp = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame_cpu_temp.add(vbox_cpu_temp)

        # CPU Average Temperature Label
        self.cpu_avg_label = Gtk.Label()
        self.cpu_avg_label.set_markup("<span font='24' weight='bold' >CPU Avg: Loading...</span>")
        vbox_cpu_temp.pack_start(self.cpu_avg_label, False, False, 5)

       # CPU Temperature Graph
        self.fig_temp, self.ax_temp = plt.subplots()
        self.canvas_temp = FigureCanvas(self.fig_temp)
        self.fig_temp.patch.set_facecolor('#2E2E2E')  # Dark background for the figure
        self.ax_temp.set_facecolor('#2E2E2E')  # Dark background for the plot area
        self.ax_temp.set_ylabel("°C", color='#FFC107')
        self.ax_temp.set_ylim(30, 100)
        self.ax_temp.tick_params(axis='x', colors='#FFC107')
        self.ax_temp.tick_params(axis='y', colors='#FFC107')
        self.ax_temp.grid(True, linestyle='--', linewidth=0.5, color='gray')
        self.cpu_temp_data = deque(maxlen=100)
        self.line_temp, = self.ax_temp.plot([], [], 'red')  # Keep red for temperature visibility
        vbox_cpu_temp.pack_start(self.canvas_temp, True, True, 5)       

        # Attach the frame to the grid
        grid.attach_next_to(frame_cpu_temp, frame_sys_info, Gtk.PositionType.RIGHT, 3, 3)


        # Create a frame for Sensors Data
        frame_sensors = Gtk.Frame(label="All Sensor Temperatures")
        frame_sensors.set_label_align(0.5, 0.5)
        frame_sensors.set_margin_bottom(10)
        frame_sensors.set_margin_start(10)
        frame_sensors.set_margin_end(10)

        # Create a grid for sensor labels inside the frame
        self.sensor_grid = Gtk.Grid()
        self.sensor_grid.set_column_spacing(60)
        self.sensor_grid.set_row_spacing(5)
        frame_sensors.add(self.sensor_grid)

        # Attach the frame to the main grid
        grid.attach_next_to(frame_sensors, frame_cpu_temp, Gtk.PositionType.RIGHT, 10, 5)

        # Define sensors
        self.components = {
            "Core 0": get_core0, "Core 1": get_core1, "Core 2": get_core2, "Core 3": get_core3,
            "Sensor 1": get_temp1, "Sensor 2": get_temp2, "Sensor 3": get_temp3,
            "Sensor 4": get_temp4, "Sensor 5": get_temp5, "Sensor 6": get_temp6,
        }
        self.labels = {}

        # Populate grid with sensor names and values
        for i, (name, func) in enumerate(self.components.items()):
            # Sensor name label
            label_name = Gtk.Label()
            label_name.set_markup(f"<span font='14' color='#FFC107'>{name}</span>")  # Increased font
            label_name.set_xalign(1)
            label_name.set_margin_top(10)
            label_name.set_margin_start(15)  
            label_name.set_margin_end(15)
            self.sensor_grid.attach(label_name, 0, i, 1, 1)

            # Sensor value label
            label_value = Gtk.Label()
            label_value.set_markup("<span font='14' color='#FFC107'>Loading...</span>")  # Increased font
            label_value.set_xalign(0)
            self.sensor_grid.attach(label_value, 1, i, 1, 1)
            label_value.set_margin_top(10)
            label_value.set_margin_start(15)  # Adds padding on the left
            label_value.set_margin_end(15)    # Adds padding on the right
            self.labels[name] = label_value



        # Create a frame for CPU Usage Graph
        frame_cpu_usage = Gtk.Frame(label="CPU Usage")
        frame_cpu_usage.set_label_align(0.5, 0.5)

        # Create a box inside the frame to hold the graph
        vbox_cpu_usage = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame_cpu_usage.add(vbox_cpu_usage)

        # CPU Usage Graph
        self.fig_usage, self.ax_usage = plt.subplots()
        self.canvas_usage = FigureCanvas(self.fig_usage)
        self.fig_usage.patch.set_facecolor('#2E2E2E')  # Dark background for figure
        self.ax_usage.set_facecolor('#2E2E2E')  # Dark background for plot area
        self.ax_usage.set_title("CPU Usage Over Time", color='#FFC107')
        self.ax_usage.set_ylim(0, 100)
        self.ax_usage.tick_params(axis='x', colors='#FFC107')
        self.ax_usage.tick_params(axis='y', colors='#FFC107')
        self.ax_usage.grid(True, linestyle='--', linewidth=0.5, color='gray')
        self.cpu_usage_data = deque(maxlen=100)
        self.line_usage, = self.ax_usage.plot([], [], 'cyan')  # Cyan for better visibility
        # Add the canvas to the frame
        vbox_cpu_usage.pack_start(self.canvas_usage, True, True, 5)

        # Attach the frame to the grid
        grid.attach(frame_cpu_usage,1,5, 13, 20)
        # Create a frame for Fan Speed
        frame_fan = Gtk.Frame(label="Fan Speed")
        frame_fan.set_label_align(0.5, 0.5)

        # Create a box inside the frame to hold the label
        vbox_fan = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame_fan.add(vbox_fan)

        # Fan Speed Label
        self.fan_label = Gtk.Label()
        self.fan_label.set_markup("<span font='18' weight='bold' color='#FFC107'>Loading...</span>")
        self.fan_label.set_halign(Gtk.Align.CENTER)
        vbox_fan.pack_start(self.fan_label, True, True, 5)

        # Attach the frame to the grid
        grid.attach(frame_fan,0,2, 1, 1)

        # Create a frame for Disk Usage Graph
        frame_disk_usage = Gtk.Frame(label="Disk Usage")
        frame_disk_usage.set_label_align(0.5, 0.5)

        # Create a box inside the frame to hold the graph
        vbox_disk_usage = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame_disk_usage.add(vbox_disk_usage)

        # Generate the Disk Usage Graph
        self.fig_disk = create_disk_graph()
        self.canvas_disk = FigureCanvas(self.fig_disk)

        # Add the canvas to the frame
        vbox_disk_usage.pack_start(self.canvas_disk, True, True, 5)

        # Attach the frame to the grid
        grid.attach_next_to(frame_disk_usage, frame_fan, Gtk.PositionType.BOTTOM, 1, 22)

        # Start Updates
        GLib.timeout_add(1000, self.update_sensors)
        self.anim_temp = animation.FuncAnimation(self.fig_temp, self.update_cpu_temp_graph,cache_frame_data=False, interval=1000)
        self.anim_usage = animation.FuncAnimation(self.fig_usage, self.update_cpu_usage_graph,cache_frame_data=False, interval=1000)

    def update_sensors(self):
        threading.Thread(target=self.fetch_sensor_data, daemon=True).start()
        return True

    def fetch_sensor_data(self):
        core_temps = [float(get_core0().split()[0]), float(get_core1().split()[0]),
                      float(get_core2().split()[0]), float(get_core3().split()[0])]
        avg_cpu_temp = sum(core_temps) / len(core_temps)
        temp_color = "cyan"  # Default (Yellow)
        if avg_cpu_temp > 75:
            temp_color = "#FF5733"  # Change to Red when above 70°C

# Update the label with the selected color
        GLib.idle_add(
            self.cpu_avg_label.set_markup,
            f"<span font='24' weight='bold' color='{temp_color}'>CPU Avg: {avg_cpu_temp:.2f} °C</span>"
        )
        for name, func in self.components.items():
            new_value = func()
            numeric_value = re.sub(r'[^\d.]', '', new_value)
            value=float(numeric_value)
            color = "cyan"
            try:
                if value > 75:
                    color = "#FF5733"  # Red for values above 75
            except ValueError:
                pass  # If new_value is not a number, keep default color (yellow)
            GLib.idle_add(
                self.labels[name].set_markup,
                f"<span font='14' color='{color}'>{new_value}</span>"
            )

        GLib.idle_add(self.fan_label.set_markup, f"<span font='18' weight='bold' color='#FFC107'>{get_fan_speed()}</span>")
    
    def update_cpu_temp_graph(self, frame):
        self.cpu_temp_data.append(float(get_core0().split()[0]))
        self.line_temp.set_xdata(range(len(self.cpu_temp_data)))
        self.line_temp.set_ydata(self.cpu_temp_data)
        self.ax_temp.relim()
        self.ax_temp.autoscale_view()
        self.canvas_temp.draw()

    def update_cpu_usage_graph(self, frame):
        self.cpu_usage_data.append(psutil.cpu_percent())
        self.line_usage.set_xdata(range(len(self.cpu_usage_data)))
        self.line_usage.set_ydata(self.cpu_usage_data)
        self.ax_usage.relim()
        self.ax_usage.autoscale_view()
        self.canvas_usage.draw()


    def show_about_dialog(self, widget):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("CoreSense")
        about_dialog.set_version("1.0")
        about_dialog.set_copyright("© 2025 Prajit")
        about_dialog.set_comments("A GTK-based system monitoring tool displaying CPU usage, temperature, and disk stats.")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_logo_icon_name("computer")
        about_dialog.set_website("https://github.com/your-repo")  # Replace with your GitHub or project link
        about_dialog.set_website_label("Project Repository")
        about_dialog.set_authors(["Prajit"])
        about_dialog.set_documenters(["prajit2324@gmail.com"])
        about_dialog.set_transient_for(self)
        about_dialog.run()
        about_dialog.destroy()

win = SensorApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
