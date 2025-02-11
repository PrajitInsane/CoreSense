import subprocess
import psutil
import re

def check_cpu_temp(component):
    """
    Extracts the temperature of a specific component from sensors output.
    
    :param component_label: The label of the component (e.g., "Core 0:")
    :return: Temperature as a float, or None if not found.
    """
    try:
        # Get the complete sensors output
        output = subprocess.check_output("sensors", shell=True).decode()
    except subprocess.CalledProcessError as e:
        print("Error running sensors command:", e)
        return None

    # Build a regex pattern. This assumes the line looks like:
    # "Core 0:       +48.0°C  (high = +80.0°C, crit = +100.0°C)"
    pattern = re.compile(rf"{re.escape(component)}\s*:\s*\+?([0-9\.]+)°C")
    match = pattern.search(output)
    if match:
        return float(match.group(1))
    else:
        return None
    
def get_temp1():
    return str(check_cpu_temp("temp1"))+" °C"

def get_temp2():
    return str(check_cpu_temp("temp2"))+" °C"

def get_temp3():
    return str(check_cpu_temp("temp3"))+" °C"

def get_temp4():
    return str(check_cpu_temp("temp4"))+" °C"

def get_temp5():
    return str(check_cpu_temp("temp5"))+" °C"

def get_temp6():
    return str(check_cpu_temp("temp6"))+" °C"

def get_core0():
    return str(check_cpu_temp("Core 0"))+" °C"

def get_core1():
    return str(check_cpu_temp("Core 1"))+" °C"

def get_core2():
    return str(check_cpu_temp("Core 2"))+" °C"

def get_core3():
    return str(check_cpu_temp("Core 3"))+" °C"

def get_fan_speed():
    """Fetch Fan RPM."""
    try:
        output = subprocess.check_output("sensors", shell=True).decode()
        match = re.search(r"fan\d+:\s*([0-9]+)\s*RPM", output)  # Adjust regex if needed
        return f"{match.group(1)} RPM" if match else "N/A"
    except Exception:
        return "Error"

def get_cpu_usage():
    return psutil.cpu_percent()

