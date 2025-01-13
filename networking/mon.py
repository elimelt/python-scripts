import psutil
import platform
import subprocess
import json
from datetime import datetime

def get_system_info():
    metrics = {}
    
    # Basic system information
    metrics['system'] = {
        'os': platform.system(),
        'os_version': platform.mac_ver()[0],
        'hostname': platform.node(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # CPU metrics
    metrics['cpu'] = {
        'physical_cores': psutil.cpu_count(logical=False),
        'total_cores': psutil.cpu_count(logical=True),
        'cpu_freq_current': psutil.cpu_freq().current if hasattr(psutil.cpu_freq(), 'current') else None,
        'cpu_percent': psutil.cpu_percent(interval=1, percpu=True),
        'cpu_stats': dict(psutil.cpu_stats()._asdict()),
        'cpu_times_percent': dict(psutil.cpu_times_percent()._asdict())
    }
    
    # Memory metrics
    vm = psutil.virtual_memory()
    metrics['memory'] = {
        'total': vm.total,
        'available': vm.available,
        'used': vm.used,
        'percent': vm.percent,
        'swap': dict(psutil.swap_memory()._asdict())
    }
    
    # Disk metrics
    metrics['disk'] = {
        'partitions': [],
        'io_counters': dict(psutil.disk_io_counters(perdisk=True))
    }
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            metrics['disk']['partitions'].append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            })
        except PermissionError:
            continue
    
    # Network metrics
    metrics['network'] = {
        'interfaces': psutil.net_if_addrs(),
        'io_counters': dict(psutil.net_io_counters(pernic=True)),
        'connections': [conn._asdict() for conn in psutil.net_connections()]
    }
    
    # Battery information (if applicable)
    try:
        battery = psutil.sensors_battery()
        if battery:
            metrics['battery'] = {
                'percent': battery.percent,
                'power_plugged': battery.power_plugged,
                'seconds_left': battery.secsleft
            }
    except Exception:
        metrics['battery'] = None
    
    # Temperature sensors (if available)
    try:
        metrics['temperatures'] = psutil.sensors_temperatures()
    except Exception:
        metrics['temperatures'] = None
    
    # Process information
    metrics['processes'] = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            metrics['processes'].append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Additional macOS-specific metrics using system_profiler
    try:
        sp_hardware = subprocess.check_output(['system_profiler', 'SPHardwareDataType', '-json'])
        metrics['hardware_details'] = json.loads(sp_hardware)
    except Exception:
        metrics['hardware_details'] = None
    
    return metrics

def save_metrics(metrics, filename='system_metrics.json'):
    """Save metrics to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)

if __name__ == "__main__":
    metrics = get_system_info()
    save_metrics(metrics)
    print(json.dumps(metrics, indent=2, default=str))