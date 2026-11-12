import sys

from .core import listening


def main():
    socks = listening()
    if not socks:
        print("No listening TCP sockets.")
        return 0
    print(f"{'PORT':>6}  {'ADDRESS':<24} {'PID':>7}  {'PROCESS':<20} EXPOSURE")
    for s in socks:
        pid = s["pid"] if s["pid"] is not None else "-"
        print(f"{s['port']:>6}  {s['ip']:<24} {pid:>7}  {s['process']:<20} {s['scope']}")
    if any(s["pid"] is None for s in socks):
        print("\n(process shown as '-' when owned by another user; run with sudo to see all)")
    return 0


sys.exit(main())
