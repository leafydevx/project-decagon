import argparse
import shutil
import subprocess
import sys

# action -> (command prefix, needs_root)
MANAGERS = {
    "pacman": {
        "install": ["pacman", "-S"], "remove": ["pacman", "-Rs"],
        "search": ["pacman", "-Ss"], "update": ["pacman", "-Syu"],
        "info": ["pacman", "-Si"], "root": True,
    },
    "apt": {
        "install": ["apt", "install"], "remove": ["apt", "remove"],
        "search": ["apt", "search"], "update": ["apt", "update"],
        "info": ["apt", "show"], "root": True,
    },
    "dnf": {
        "install": ["dnf", "install"], "remove": ["dnf", "remove"],
        "search": ["dnf", "search"], "update": ["dnf", "upgrade"],
        "info": ["dnf", "info"], "root": True,
    },
    "zypper": {
        "install": ["zypper", "install"], "remove": ["zypper", "remove"],
        "search": ["zypper", "search"], "update": ["zypper", "update"],
        "info": ["zypper", "info"], "root": True,
    },
    "apk": {
        "install": ["apk", "add"], "remove": ["apk", "del"],
        "search": ["apk", "search"], "update": ["apk", "upgrade"],
        "info": ["apk", "info"], "root": True,
    },
}

ID_TO_MANAGER = {
    "arch": "pacman", "manjaro": "pacman", "endeavouros": "pacman", "omarchy": "pacman",
    "debian": "apt", "ubuntu": "apt", "linuxmint": "apt", "pop": "apt",
    "fedora": "dnf", "rhel": "dnf", "centos": "dnf", "rocky": "dnf", "almalinux": "dnf",
    "opensuse": "zypper", "opensuse-leap": "zypper", "opensuse-tumbleweed": "zypper", "sles": "zypper",
    "alpine": "apk",
}

READ_ONLY = {"search", "info"}


def parse_os_release(text):
    out = {}
    for line in text.splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def detect_manager(os_release):
    ids = [os_release.get("ID", "")] + os_release.get("ID_LIKE", "").split()
    for i in ids:
        if i in ID_TO_MANAGER:
            return ID_TO_MANAGER[i]
    for name in MANAGERS:  # fall back to whatever is installed
        if shutil.which(name):
            return name
    return None


def build_command(manager, action, packages, is_root, assume_yes=False):
    spec = MANAGERS[manager]
    cmd = list(spec[action])
    if assume_yes and action not in READ_ONLY:
        cmd.append("--noconfirm" if manager == "pacman" else "-y")
    cmd += list(packages)
    if spec["root"] and action not in READ_ONLY and not is_root:
        cmd = ["sudo"] + cmd
    return cmd


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pkgx", description="One command for every distro's package manager")
    ap.add_argument("action", choices=["install", "remove", "search", "update", "info"])
    ap.add_argument("packages", nargs="*")
    ap.add_argument("-n", "--dry-run", action="store_true", help="print the command instead of running it")
    ap.add_argument("-y", "--yes", action="store_true", help="don't prompt for confirmation")
    ap.add_argument("--manager", choices=sorted(MANAGERS), help="override auto-detection")
    args = ap.parse_args(argv)

    if args.action in {"install", "remove", "search", "info"} and not args.packages:
        ap.error(f"'{args.action}' needs at least one package")

    manager = args.manager
    if not manager:
        try:
            with open("/etc/os-release") as f:
                manager = detect_manager(parse_os_release(f.read()))
        except OSError:
            manager = detect_manager({})
    if not manager:
        print("pkgx: could not detect a package manager", file=sys.stderr)
        return 1

    import os
    cmd = build_command(manager, args.action, args.packages, os.geteuid() == 0, args.yes)
    if args.dry_run:
        print(" ".join(cmd))
        return 0
    return subprocess.call(cmd)
