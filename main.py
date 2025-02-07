import gi
from sensors import (
    get_temp1, get_temp2, get_temp3, get_temp4, get_temp5, get_temp6, 
    get_core0, get_core1, get_core2, get_core3, get_fan_speed
)

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class SensorApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Monitor")
        self.set_default_size(600, 450)
        self.set_border_width(10)

        # Main Vertical Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.add(vbox)

        # Average CPU Temperature Label (Top Centered)
        self.cpu_avg_label = Gtk.Label()
        self.cpu_avg_label.set_markup("<span font='24' weight='bold'>CPU Avg: Loading...</span>")
        self.cpu_avg_label.set_halign(Gtk.Align.CENTER)  # Center horizontally
        vbox.pack_start(self.cpu_avg_label, False, False, 0)

        # Create a Box to center the Grid
        grid_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        grid_container.set_halign(Gtk.Align.CENTER)  # Center the entire table

        # Grid Layout for Sensors
        grid = Gtk.Grid()
        grid.set_row_spacing(50)  # Increased row spacing
        grid.set_column_spacing(200)  # Increased column spacing

        grid_container.pack_start(grid, False, False, 0)
        vbox.pack_start(grid_container, True, True, 0)

        # Sensor Labels Dictionary
        self.labels = {}

        # Define Sensors with Functions
        self.components = {
            "Sensor 1": get_temp1, "Sensor 2": get_temp2, "Sensor 3": get_temp3,
            "Sensor 4": get_temp4, "Sensor 5": get_temp5, "Sensor 6": get_temp6,
            "Core 0": get_core0, "Core 1": get_core1, "Core 2": get_core2, "Core 3": get_core3
        }

        # Create Table-like Layout with Gaps
        for i, (name, func) in enumerate(self.components.items()):
            label_name = Gtk.Label(label=name)
            label_name.set_xalign(1)  # Align right
            grid.attach(label_name, 0, i, 1, 1)

            label_value = Gtk.Label(label="Loading...")
            label_value.set_xalign(0)  # Align left
            grid.attach(label_value, 1, i, 1, 1)

            # Store label reference
            self.labels[name] = label_value

        # Fan Speed Label (At the Bottom)
        self.fan_label = Gtk.Label()
        self.fan_label.set_markup("<span font='18' weight='bold'>Fan Speed: Loading...</span>")
        self.fan_label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(self.fan_label, False, False, 0)

        # Update sensor data every second
        GLib.timeout_add(1000, self.update_sensors)

    def update_sensors(self):
        """Update sensor readings dynamically"""
        # Calculate Average CPU Temperature
        core_temps = [float(get_core0().split()[0]), float(get_core1().split()[0]), 
                      float(get_core2().split()[0]), float(get_core3().split()[0])]
        avg_cpu_temp = sum(core_temps) / len(core_temps)

        self.cpu_avg_label.set_markup(f"<span font='36' weight='bold'>CPU Avg: {avg_cpu_temp:.2f} °C</span>")

        # Update sensor values
        for name, func in self.components.items():
            self.labels[name].set_text(func())

        # Update fan speed
        self.fan_label.set_markup(f"<span font='28' weight='bold'>Fan Speed: {get_fan_speed()}</span>")

        return True  # Continue updating

# Run the application
win = SensorApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
