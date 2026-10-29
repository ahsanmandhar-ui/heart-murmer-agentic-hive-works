import os
import psutil
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

def get_resources():
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "ram_available_mb": psutil.virtual_memory().available / (1024 * 1024),
        "ram_total_mb": psutil.virtual_memory().total / (1024 * 1024),
        "disk_free_mb": psutil.disk_usage(str(BASE)).free / (1024 * 1024),
    }

def can_proceed(min_ram_mb=500, min_disk_mb=100, max_cpu=90):
    r = get_resources()
    if r["ram_available_mb"] < min_ram_mb:
        return False, f"Low RAM: {r['ram_available_mb']:.0f} MB < {min_ram_mb} MB"
    if r["disk_free_mb"] < min_disk_mb:
        return False, f"Low disk: {r['disk_free_mb']:.0f} MB < {min_disk_mb} MB"
    if r["cpu_percent"] > max_cpu:
        return False, f"High CPU: {r['cpu_percent']:.0f}% > {max_cpu}%"
    return True, "OK"

def wait_for_resources(min_ram_mb=500, min_disk_mb=100, max_cpu=90, timeout=60):
    import time
    start = time.time()
    while time.time() - start < timeout:
        ok, msg = can_proceed(min_ram_mb, min_disk_mb, max_cpu)
        if ok:
            return True, msg
        time.sleep(2)
    return False, f"Timeout waiting for resources: {msg}"

if __name__ == "__main__":
    import sys
    r = get_resources()
    print(json.dumps(r, indent=2))
    ok, msg = can_proceed()
    print(f"Can proceed: {ok} ({msg})")
