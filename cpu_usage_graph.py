import matplotlib.pyplot as plt
import matplotlib.animation as animation
import psutil

cpu_usage_history = []

def update(frame):
    cpu_usage_history.append(psutil.cpu_percent())

    if len(cpu_usage_history) > 30:
        cpu_usage_history.pop(0)

    plt.cla()
    plt.gca().set_facecolor('#2E2E2E')  # Set background for the plot area
    plt.plot(cpu_usage_history, marker='o', linestyle='-', color='cyan', label="CPU Usage (%)")
    plt.xlabel("Time (s)", color='white')
    plt.ylabel("CPU Usage (%)", color='white')
    plt.title("CPU Usage Over Time", color='white')
    plt.legend(facecolor='#444444', edgecolor='white')  # Dark legend background
    plt.grid(True, color='gray')

    plt.xticks(color='white')
    plt.yticks(color='white')

def create_cpu_usage_graph():
    """Create and return a figure with a persistent animation object."""
    fig = plt.figure(figsize=(4, 2))
    fig.patch.set_facecolor('#2E2E2E')  # Set background color for the figure
    
    global ani_usage  # ✅ Store animation in a global variable
    ani_usage = animation.FuncAnimation(fig, update, interval=1000, cache_frame_data=False)
    
    return fig
