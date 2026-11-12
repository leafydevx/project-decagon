"""Read-only security checks. Each returns a list of (severity, message)."""

import os
import stat

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"


def parse_sshd_config(text):
    """First occurrence of each directive wins, like sshd. Keys lowercased."""
    cfg = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            cfg.setdefault(parts[0].lower(), parts[1].strip().lower())
    return cfg


def check_sshd(text):
    cfg = parse_sshd_config(text)
    results = []
    root = cfg.get("permitrootlogin", "prohibit-password")
    results.append((FAIL, "SSH allows root login with a password") if root == "yes"
                   else (PASS, f"PermitRootLogin = {root}"))
    results.append((WARN, "SSH password authentication is enabled") if cfg.get("passwordauthentication", "yes") == "yes"
                   else (PASS, "SSH password authentication disabled"))
    if cfg.get("permitemptypasswords") == "yes":
        results.append((FAIL, "SSH permits empty passwords"))
    return results


def check_passwd(text):
    results = []
    extra = []
    for line in text.splitlines():
        f = line.split(":")
        if len(f) >= 3 and f[2] == "0" and f[0] != "root":
            extra.append(f[0])
    results.append((FAIL, f"Extra UID 0 accounts: {', '.join(extra)}") if extra
                   else (PASS, "Only root has UID 0"))
    return results


def check_mode(path, max_mode, label=None):
    label = label or path
    try:
        mode = stat.S_IMODE(os.stat(path).st_mode)
    except FileNotFoundError:
        return [(PASS, f"{label} not present")]
    except OSError as e:
        return [(WARN, f"Cannot stat {label}: {e.strerror}")]
    if mode & ~max_mode:
        return [(FAIL, f"{label} is {mode:04o}, should be at most {max_mode:04o}")]
    return [(PASS, f"{label} permissions {mode:04o}")]


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return None


def run_all():
    results = []
    sshd = read("/etc/ssh/sshd_config")
    results += check_sshd(sshd) if sshd is not None else [(PASS, "No readable sshd_config (SSH server likely not installed)")]
    passwd = read("/etc/passwd")
    if passwd is not None:
        results += check_passwd(passwd)
    results += check_mode("/etc/shadow", 0o640)
    results += check_mode("/etc/passwd", 0o644)
    results += check_mode("/etc/sudoers", 0o440)
    return results
