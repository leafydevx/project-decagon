"""snapback — Linux backup, OS snapshot, and bootable clone tool."""

import argparse
import sys
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _require_root(cmd_name):
    if os.geteuid() != 0:
        print(f"error: '{cmd_name}' requires root (run with sudo)", file=sys.stderr)
        sys.exit(1)


def _ok(results):
    """Return True if all (step, rc) pairs passed."""
    return all(rc == 0 for _, rc in results)


def _report(results):
    for step, rc in results:
        status = "OK" if rc == 0 else f"FAILED (exit {rc})"
        print(f"  {step:<20} {status}")


# ---------------------------------------------------------------------------
# sub-commands
# ---------------------------------------------------------------------------

def cmd_backup(args):
    from .backup import run_backup, list_backups

    sources = [Path(s) for s in args.sources]
    for s in sources:
        if not s.exists():
            print(f"error: source does not exist: {s}", file=sys.stderr)
            sys.exit(1)

    dest_dir, result = run_backup(
        sources=sources,
        dest=args.dest,
        incremental=not args.full,
        exclude=args.exclude or [],
        dry_run=args.dry_run,
        progress=args.progress,
    )

    if args.dry_run:
        print("[dry-run] No files were actually copied.")
    elif result.returncode == 0:
        print(f"Backup complete → {dest_dir}")
    else:
        print(f"Backup failed (rsync exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def cmd_snapshot(args):
    _require_root("snapshot")

    if args.image:
        from .snapshot import snapshot_to_image
        print(f"Creating bootable image: {args.image}")
        print("This may take a long time — do not interrupt.\n")
        results = snapshot_to_image(
            output_image=args.image,
            size_mb=args.size,
            dry_run=args.dry_run,
        )
        _report(results)
        if not _ok(results):
            sys.exit(1)
        print(f"\nImage ready: {args.image}")
        print("Write to a USB/disk with:")
        print(f"  sudo dd if={args.image} of=/dev/sdX bs=4M status=progress")
    else:
        from .snapshot import snapshot_os
        print(f"Snapshotting OS → {args.dest}")
        print("This may take a long time — do not interrupt.\n")
        result = snapshot_os(
            dest=args.dest,
            dry_run=args.dry_run,
            progress=args.progress,
        )
        if result.returncode == 0:
            print(f"\nSnapshot complete → {args.dest}")
        else:
            print(f"\nSnapshot failed (exit {result.returncode})", file=sys.stderr)
            sys.exit(result.returncode)


def cmd_clone(args):
    _require_root("clone")
    from .bootable import clone_to_disk

    print(f"Cloning OS → {args.device}")
    print("WARNING: This will OVERWRITE data on the target device!")
    if not args.yes:
        confirm = input("Type 'yes' to continue: ").strip()
        if confirm != "yes":
            print("Aborted.")
            sys.exit(0)

    results = clone_to_disk(
        dest_device=args.device,
        mount_point=args.mount,
        grub_target=args.grub_target,
        dry_run=args.dry_run,
        progress=args.progress,
    )
    _report(results)
    if _ok(results):
        print(f"\nClone complete. {args.device} is bootable.")
    else:
        print("\nClone encountered errors.", file=sys.stderr)
        sys.exit(1)


def cmd_restore(args):
    if args.pick:
        from .restore import pick_backup, restore_backup
        chosen = pick_backup(args.backup)
        if chosen is None:
            sys.exit(0)
        backup_dir = chosen
    else:
        backup_dir = args.backup

    from .restore import restore_backup
    print(f"Restoring {backup_dir} → {args.dest}")
    result = restore_backup(
        backup_dir=backup_dir,
        dest=args.dest,
        dry_run=args.dry_run,
        progress=args.progress,
    )
    if result.returncode == 0:
        print("Restore complete.")
    else:
        print(f"Restore failed (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def cmd_list(args):
    from .backup import list_backups
    import subprocess

    backups = list_backups(args.dest)
    if not backups:
        print(f"No backups found in {args.dest}")
        return

    print(f"Backups in {args.dest} (newest first):\n")
    for b in backups:
        r = subprocess.run(["du", "-sh", str(b)], capture_output=True, text=True)
        size = r.stdout.split()[0] if r.returncode == 0 else "?"
        print(f"  {b.name}  {size:>8}")


# ---------------------------------------------------------------------------
# argument parsing
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        prog="snapback",
        description="Linux backup, OS snapshot, and bootable clone tool",
    )
    p.add_argument("--version", action="version", version="snapback 0.1.0")
    sub = p.add_subparsers(dest="command", required=True)

    # --- backup ---
    bp = sub.add_parser("backup", help="Backup selected folders")
    bp.add_argument("sources", nargs="+", metavar="SOURCE",
                    help="Directories to back up")
    bp.add_argument("dest", metavar="DEST",
                    help="Destination directory (backups stored as timestamped subdirs)")
    bp.add_argument("--full", action="store_true",
                    help="Full backup (no --link-dest incremental)")
    bp.add_argument("--exclude", action="append", metavar="PATTERN",
                    help="Exclude pattern (rsync syntax, repeatable)")
    bp.add_argument("--dry-run", action="store_true",
                    help="Show what would be done without copying")
    bp.add_argument("--progress", action="store_true",
                    help="Show rsync file-transfer progress")
    bp.set_defaults(func=cmd_backup)

    # --- snapshot ---
    sp = sub.add_parser("snapshot",
                        help="Full OS snapshot (file-level, needs root)")
    sp.add_argument("dest", nargs="?", metavar="DEST",
                    help="Destination directory for file-level snapshot")
    sp.add_argument("--image", metavar="FILE.img",
                    help="Create a bootable disk image instead of a directory clone")
    sp.add_argument("--size", type=int, metavar="MB",
                    help="Image size in MB (auto-detected from df if omitted)")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--progress", action="store_true")
    sp.set_defaults(func=cmd_snapshot)

    # --- clone ---
    cp = sub.add_parser("clone",
                        help="Clone running OS to a physical disk (bootable, needs root)")
    cp.add_argument("device", metavar="DEVICE",
                    help="Target partition, e.g. /dev/sdb1")
    cp.add_argument("--mount", metavar="PATH",
                    help="Mount point (default /mnt/snapback_clone)")
    cp.add_argument("--grub-target", default="i386-pc",
                    metavar="TARGET",
                    help="GRUB target (default: i386-pc; use x86_64-efi for UEFI)")
    cp.add_argument("--yes", action="store_true",
                    help="Skip confirmation prompt")
    cp.add_argument("--dry-run", action="store_true")
    cp.add_argument("--progress", action="store_true")
    cp.set_defaults(func=cmd_clone)

    # --- restore ---
    rp = sub.add_parser("restore", help="Restore a backup to a directory")
    rp.add_argument("backup", metavar="BACKUP",
                    help="Backup snapshot directory (or backup root with --pick)")
    rp.add_argument("dest", metavar="DEST",
                    help="Restore destination")
    rp.add_argument("--pick", action="store_true",
                    help="Interactively pick a snapshot from the backup root")
    rp.add_argument("--dry-run", action="store_true")
    rp.add_argument("--progress", action="store_true")
    rp.set_defaults(func=cmd_restore)

    # --- list ---
    lp = sub.add_parser("list", help="List available backups")
    lp.add_argument("dest", metavar="DEST",
                    help="Backup destination root to list")
    lp.set_defaults(func=cmd_list)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
