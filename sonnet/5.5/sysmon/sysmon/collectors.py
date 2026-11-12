"""Read system stats straight from /proc and the filesystem (Linux only)."""

import os
import shutil
import time


def parse_meminfo(text):
    info = {}
    for line in text.splitlines():
        key, _, rest = line.partition(":")
        parts = rest.split()
        if parts:
            info[key] = int(parts[0]) * 1024  # kB -> bytes
    return info


def memory():
    with open("/proc/meminfo") as f:
        info = parse_meminfo(f.read())
    total = info["MemTotal"]
    available = info.get("MemAvailable", info["MemFree"])
    swap_total = info.get("SwapTotal", 0)
    swap_free = info.get("SwapFree", 0)
    return {
        "total": total,
        "used": total - available,
        "swap_total": swap_total,
        "swap_used": swap_total - swap_free,
    }


def parse_cpu_times(text):
    fields = text.splitlines()[0].split()[1:]
    values = [int(v) for v in fields]
    idle = values[3] + (values[4] if len(values) > 4 else 0)  # idle + iowait
    return idle, sum(values)


def cpu_percent(interval=0.5):
    with open("/proc/stat") as f:
        idle1, total1 = parse_cpu_times(f.read())
    time.sleep(interval)
    with open("/proc/stat") as f:
        idle2, total2 = parse_cpu_times(f.read())
    dt = total2 - total1
    return 0.0 if dt <= 0 else 100.0 * (1 - (idle2 - idle1) / dt)


def load_average():
    return os.getloadavg()


def uptime_seconds():
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])


def disks(paths=("/",)):
    result = []
    for path in paths:
        try:
            u = shutil.disk_usage(path)
        except OSError:
            continue
        result.append({"path": path, "total": u.total, "used": u.used})
    return result


def top_processes(n=5):
    """Top-n processes by resident memory."""
    page = os.sysconf("SC_PAGE_SIZE")
    procs = []
    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            with open(f"/proc/{pid}/stat") as f:
                stat = f.read()
            # comm is parenthesised and may contain spaces; split around it
            name = stat[stat.index("(") + 1 : stat.rindex(")")]
            rest = stat[stat.rindex(")") + 2 :].split()
            rss = int(rest[21]) * page
        except (OSError, ValueError, IndexError):
            continue
        procs.append({"pid": int(pid), "name": name, "rss": rss})
    procs.sort(key=lambda p: p["rss"], reverse=True)
    return procs[:n]
