import argparse
import re
import sys
from collections import Counter

# 127.0.0.1 - - [10/Oct/2025:13:55:36 +0000] "GET /x HTTP/1.1" 200 2326
ACCESS_RE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>[A-Z]+) (?P<path>\S+)[^"]*" (?P<status>\d{3}) (?P<size>\S+)'
)
# Nov 11 12:00:01 host sshd[123]: Failed password for root from 1.2.3.4 port 22 ssh2
SYSLOG_RE = re.compile(r"^(?P<time>\w{3}\s+\d+ [\d:]+) (?P<host>\S+) (?P<proc>[^\[:\s]+)(?:\[\d+\])?: (?P<msg>.*)$")
LEVEL_RE = re.compile(r"\b(DEBUG|INFO|NOTICE|WARN(?:ING)?|ERR(?:OR)?|CRIT(?:ICAL)?|FATAL)\b", re.I)
FAILED_RE = re.compile(r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+)")


def analyze(lines):
    stats = {
        "total": 0, "unparsed": 0, "levels": Counter(), "status": Counter(),
        "ips": Counter(), "paths": Counter(), "processes": Counter(), "failed_logins": Counter(),
    }
    for line in lines:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        stats["total"] += 1
        m = ACCESS_RE.match(line)
        if m:
            stats["status"][m["status"]] += 1
            stats["ips"][m["ip"]] += 1
            stats["paths"][m["path"]] += 1
            continue
        m = SYSLOG_RE.match(line)
        if m:
            stats["processes"][m["proc"]] += 1
            f = FAILED_RE.search(m["msg"])
            if f:
                stats["failed_logins"][f["ip"]] += 1
            lv = LEVEL_RE.search(m["msg"])
            if lv:
                stats["levels"][lv.group(1).upper()] += 1
            continue
        lv = LEVEL_RE.search(line)
        if lv:
            stats["levels"][lv.group(1).upper()] += 1
        else:
            stats["unparsed"] += 1
    return stats


def section(title, counter, n):
    if not counter:
        return []
    out = ["", title]
    out += [f"  {count:>7}  {key}" for key, count in counter.most_common(n)]
    return out


def render(stats, top=5):
    lines = [f"Lines analyzed: {stats['total']} (unparsed: {stats['unparsed']})"]
    lines += section("Log levels", stats["levels"], top)
    lines += section("HTTP status codes", stats["status"], top)
    lines += section("Top client IPs", stats["ips"], top)
    lines += section("Top paths", stats["paths"], top)
    lines += section("Top processes", stats["processes"], top)
    lines += section("Failed SSH logins by IP", stats["failed_logins"], top)
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="logsift", description="Summarize syslog and web access logs")
    ap.add_argument("files", nargs="*", help="log files (default: stdin)")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args(argv)

    def lines():
        if not args.files:
            yield from sys.stdin
        for path in args.files:
            with open(path, errors="replace") as f:
                yield from f

    try:
        print(render(analyze(lines()), args.top))
    except OSError as e:
        print(f"logsift: {e}", file=sys.stderr)
        return 1
    return 0
