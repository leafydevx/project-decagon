"""Incremental folder backup using rsync."""

import subprocess
import shutil
import os
from datetime import datetime
from pathlib import Path


def _rsync_available():
    return shutil.which("rsync") is not None


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def run_backup(sources, dest, incremental=True, exclude=None, dry_run=False, progress=False):
    """
    Rsync one or more source paths into dest/<timestamp>/.
    With incremental=True, hard-links unchanged files from the last backup (--link-dest).
    Returns (dest_dir, completed_process).
    """
    if not _rsync_available():
        raise RuntimeError("rsync not found — install it and retry")

    dest_root = Path(dest)
    dest_root.mkdir(parents=True, exist_ok=True)

    ts = _timestamp()
    dest_dir = dest_root / ts
    dest_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["rsync", "-aHAXS", "--numeric-ids", "--delete"]

    if progress:
        cmd.append("--progress")

    if dry_run:
        cmd.append("--dry-run")

    # hard-link unchanged files from the most recent prior backup
    if incremental:
        link_dest = _latest_backup(dest_root, exclude=ts)
        if link_dest:
            cmd += ["--link-dest", str(link_dest)]

    for pat in (exclude or []):
        cmd += ["--exclude", pat]

    for src in sources:
        # trailing slash: copy contents, not the dir itself
        s = str(src).rstrip("/") + "/"
        cmd.append(s)

    cmd.append(str(dest_dir) + "/")

    result = subprocess.run(cmd)
    return dest_dir, result


def _latest_backup(dest_root, exclude=None):
    """Return the most recent timestamped backup dir, or None."""
    dirs = sorted(
        (d for d in Path(dest_root).iterdir()
         if d.is_dir() and d.name != exclude),
        reverse=True
    )
    return dirs[0] if dirs else None


def list_backups(dest):
    """Return sorted list of backup dir paths (newest first)."""
    root = Path(dest)
    if not root.exists():
        return []
    return sorted(
        (d for d in root.iterdir() if d.is_dir()),
        reverse=True
    )


def delete_backup(backup_dir):
    """Remove a backup directory (uses rm -rf via Python)."""
    import shutil as _sh
    _sh.rmtree(str(backup_dir))
