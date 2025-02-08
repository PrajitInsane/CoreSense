import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

def get_disks_usage():
    """Fetch all disk partitions and their usage stats."""
    try:
        usage = psutil.disk_usage("/")
        total = round(usage.total / (1024 ** 3), 1)  # Convert bytes to GB
        used = round(usage.used / (1024 ** 3), 1)
        free = round(usage.free / (1024 ** 3), 1)
        return used, free, total
    except PermissionError:
        return 0, 0, 0 

def create_disk_graph():
    used, free, total = get_disks_usage()

    fig, ax = plt.subplots(figsize=(4, 3))  # Adjust size for GTK
    labels = [f"Used ({used}GB)", f"Free ({free}GB)"]
    sizes = [used, free]
    colors = ["red", "green"]

    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.set_title(f"Disk Usage - Main Disk ({total}GB)")

    return fig
