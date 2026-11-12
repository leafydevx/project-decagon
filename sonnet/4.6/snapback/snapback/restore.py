"""Restore a folder backup or OS snapshot."""

import subprocess
import shutil
from pathlib import Path
from .backup import list_backups


def restore_backup(backup_dir, dest, dry_run=False, progress=False):
    """
    Rsync a snapshot directory back to dest.
    dest can be the original source path or any directory.
    Returns completed_process.
    """
    if not shutil.which("rsync"):
        raise RuntimeError("rsync not found")

    src = Path(backup_dir)
    if not src.exists():
        raise FileNotFoundError(f"backup not found: {backup_dir}")

    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)

    cmd = ["rsync", "-aHAXS", "--numeric-ids"]

    if progress:
        cmd.append("--progress")

    if dry_run:
        cmd.append("--dry-run")

    cmd += [str(src).rstrip("/") + "/", str(dest_path).rstrip("/") + "/"]

    return subprocess.run(cmd)


def pick_backup(dest_root):
    """
    Interactive picker: list backups in dest_root and let the user choose one.
    Returns chosen Path or None if none exist / user aborts.
    """
    backups = list_backups(dest_root)
    if not backups:
        print(f"No backups found in {dest_root}")
        return None

    print("Available backups (newest first):")
    for i, b in enumerate(backups, 1):
        size = _dir_size_human(b)
        print(f"  [{i}] {b.name}  ({size})")

    raw = input("Choose number (or q to quit): ").strip()
    if raw.lower() == "q":
        return None

    try:
        idx = int(raw) - 1
        return backups[idx]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return None


def _dir_size_human(path):
    r = subprocess.run(
        ["du", "-sh", str(path)],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        return r.stdout.split()[0]
    return "?"
