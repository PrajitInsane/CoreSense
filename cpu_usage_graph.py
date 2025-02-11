import matplotlib.pyplot as plt
import matplotlib.animation as animation
import psutil

cpu_usage_history = []

def update(frame):
    cpu_usage_history.append(psutil.cpu_percent())

    if len(cpu_usage_history) > 30:
        cpu_usage_history.pop(0)

    plt.cla()
    plt.plot(cpu_usage_history, marker='o', linestyle='-', color='b', label="CPU Usage (%)")
    plt.xlabel("Time (s)")
    plt.ylabel("CPU Usage (%)")
    plt.title("CPU Usage Over Time")
    plt.legend()
    plt.grid(True)

def create_cpu_usage_graph():
    """Create and return a figure with a persistent animation object."""
    fig = plt.figure(figsize=(4, 2))
    global ani_usage  # ✅ Store animation in a global variable
    ani_usage = animation.FuncAnimation(fig, update, interval=1000, cache_frame_data=False)
    return fig
