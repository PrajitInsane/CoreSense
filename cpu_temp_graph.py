import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sensors import get_core0, get_core1, get_core2, get_core3

cpu_temp_history = []

def get_avg_cpu_temp():
    core_temps = [float(get_core0().split()[0]), float(get_core1().split()[0]),
                  float(get_core2().split()[0]), float(get_core3().split()[0])]
    return sum(core_temps) / len(core_temps)

def update(frame):
    cpu_temp_history.append(get_avg_cpu_temp())

    if len(cpu_temp_history) > 30:
        cpu_temp_history.pop(0)

    plt.cla()
    plt.plot(cpu_temp_history, marker='o', linestyle='-', color='r', label="CPU Avg Temp (°C)")
    plt.xlabel("Time (s)")
    plt.ylabel("Temperature (°C)")
    plt.title("CPU Temperature Over Time")
    plt.legend()
    plt.grid(True)

def create_cpu_temp_graph():
    """Create and return a figure with a persistent animation object."""
    fig = plt.figure(figsize=(4, 2))
    global ani  # ✅ Store animation in a global variable to prevent garbage collection
    ani = animation.FuncAnimation(fig, update, interval=1000, cache_frame_data=False)
    return fig
