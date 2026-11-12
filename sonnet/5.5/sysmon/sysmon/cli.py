import argparse
import json
import sys
import time

from . import collectors


def human_bytes(n):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024 or unit == "TiB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def human_duration(seconds):
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    parts = [f"{days}d"] if days else []
    return " ".join(parts + [f"{hours}h", f"{minutes}m"])


def bar(percent, width=20):
    filled = round(width * percent / 100)
    return "[" + "#" * filled + "-" * (width - filled) + f"] {percent:5.1f}%"


def snapshot(top, interval):
    mem = collectors.memory()
    return {
        "cpu_percent": collectors.cpu_percent(interval),
        "load_average": collectors.load_average(),
        "uptime_seconds": collectors.uptime_seconds(),
        "memory": mem,
        "disks": collectors.disks(),
        "top_processes": collectors.top_processes(top),
    }


def render(s):
    mem = s["memory"]
    lines = [
        f"Uptime : {human_duration(s['uptime_seconds'])}",
        "Load   : " + " ".join(f"{x:.2f}" for x in s["load_average"]),
        f"CPU    : {bar(s['cpu_percent'])}",
        f"Memory : {bar(100 * mem['used'] / mem['total'])} "
        f"({human_bytes(mem['used'])} / {human_bytes(mem['total'])})",
    ]
    if mem["swap_total"]:
        lines.append(
            f"Swap   : {bar(100 * mem['swap_used'] / mem['swap_total'])} "
            f"({human_bytes(mem['swap_used'])} / {human_bytes(mem['swap_total'])})"
        )
    for d in s["disks"]:
        lines.append(
            f"Disk {d['path']:<4}: {bar(100 * d['used'] / d['total'])} "
            f"({human_bytes(d['used'])} / {human_bytes(d['total'])})"
        )
    lines.append("")
    lines.append(f"{'PID':>7}  {'RSS':>10}  NAME")
    for p in s["top_processes"]:
        lines.append(f"{p['pid']:>7}  {human_bytes(p['rss']):>10}  {p['name']}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sysmon", description="Tiny Linux system monitor")
    ap.add_argument("--json", action="store_true", help="print one JSON snapshot and exit")
    ap.add_argument("--watch", type=float, metavar="SECS", help="refresh every SECS seconds")
    ap.add_argument("--top", type=int, default=5, help="number of processes to show (default 5)")
    args = ap.parse_args(argv)

    if not sys.platform.startswith("linux"):
        ap.exit(1, "sysmon only supports Linux (/proc required)\n")

    if args.json:
        print(json.dumps(snapshot(args.top, 0.5), indent=2))
        return 0

    try:
        while True:
            out = render(snapshot(args.top, 0.5))
            if args.watch:
                sys.stdout.write("\033[2J\033[H")
            print(out)
            if not args.watch:
                return 0
            time.sleep(args.watch)
    except KeyboardInterrupt:
        return 0
