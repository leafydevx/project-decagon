import sys

from .checks import FAIL, PASS, WARN, run_all


def main():
    results = run_all()
    for sev, msg in results:
        print(f"[{sev}] {msg}")
    fails = sum(1 for s, _ in results if s == FAIL)
    warns = sum(1 for s, _ in results if s == WARN)
    passes = sum(1 for s, _ in results if s == PASS)
    print(f"\n{passes} passed, {warns} warnings, {fails} failures")
    return 1 if fails else 0


sys.exit(main())
