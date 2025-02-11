import platform
import psutil
import subprocess

def get_cpu_model():
    """Returns the detailed CPU model (Intel, AMD, etc.)."""
    try:
        cpu_model = subprocess.check_output("lscpu | grep 'Model name'", shell=True).decode().strip()
        return cpu_model.split(":")[1].strip() if ":" in cpu_model else "Unknown CPU"
    except Exception:
        return "Unknown CPU"

def get_gpu_model():
    """Returns the GPU model (Intel, AMD, NVIDIA)."""
    try:
        gpu_model = subprocess.check_output("lspci | grep -i '3D'", shell=True).decode().strip()
        gpu_model = gpu_model.split(":")[3].strip() if ":" in gpu_model else "Unknown GPU"
    except Exception:
        gpu_model = "Unknown GPU"

    # Check for NVIDIA GPU for more precise info
    try:
        nvidia_gpu = subprocess.check_output("nvidia-smi --query-gpu=name --format=csv,noheader", shell=True).decode().strip()
        if nvidia_gpu:
            gpu_model = nvidia_gpu  # Override lspci result
    except Exception:
        pass  # Ignore if nvidia-smi is not available

    return gpu_model

def get_ram_size():
    """Returns total RAM size in GB."""
    return round(psutil.virtual_memory().total / (1024 ** 3), 1)  # Convert bytes to GB

def get_system_info():
    """Fetch system information including CPU, GPU, RAM, and OS."""
    os_info = platform.system() + " " + platform.version()[4:11]
    cpu_model = get_cpu_model()
    gpu_model = get_gpu_model()
    ram = get_ram_size()

    return f"""
    <span font='14'>OS: {os_info}</span>\n
    <span font='14'>CPU: {cpu_model}</span>\n
    <span font='14'>RAM: {ram} GB</span>\n
    <span font='14'>GPU: {gpu_model}</span>
    """

if __name__ == "__main__":
    print(get_system_info())  # For testing
