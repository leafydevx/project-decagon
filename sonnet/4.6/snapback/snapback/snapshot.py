"""Full OS file-system snapshot (rsync-based, not block-level dd)."""

import subprocess
import shutil
from pathlib import Path
from .backup import _timestamp

# Directories that must not be included in an OS clone
_DEFAULT_EXCLUDES = [
    "/proc/*",
    "/sys/*",
    "/dev/*",
    "/run/*",
    "/tmp/*",
    "/mnt/*",
    "/media/*",
    "/lost+found",
    "/swapfile",
    "*.swp",
]


def snapshot_os(dest, extra_excludes=None, dry_run=False, progress=False):
    """
    Clone the live root filesystem to dest using rsync.
    dest must be a mounted partition or an existing directory.
    Returns completed_process.
    """
    if not shutil.which("rsync"):
        raise RuntimeError("rsync not found")

    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)

    excludes = list(_DEFAULT_EXCLUDES) + (extra_excludes or [])

    cmd = ["rsync", "-aHAXS", "--numeric-ids", "--delete"]

    if progress:
        cmd.append("--progress")

    if dry_run:
        cmd.append("--dry-run")

    for pat in excludes:
        cmd += ["--exclude", pat]

    cmd += ["/", str(dest_path) + "/"]

    return subprocess.run(cmd)


def snapshot_to_image(output_image, source_dir="/", size_mb=None, dry_run=False):
    """
    Create a bootable disk image:
      1. Create a raw image file (fallocate)
      2. Format it with a single ext4 partition + MBR
      3. Mount and rsync the OS into it
      4. Install GRUB inside the image
    Requires: parted, mkfs.ext4, grub-install, losetup (root)
    Returns list of (step, returncode).
    """
    for tool in ("parted", "mkfs.ext4", "grub-install", "losetup", "mount"):
        if not shutil.which(tool):
            raise RuntimeError(f"{tool} not found — install it")

    results = []
    img = Path(output_image)

    if dry_run:
        print(f"[dry-run] Would create image: {img}")
        return results

    # 1. Allocate image
    if size_mb is None:
        size_mb = _estimate_root_mb() + 512  # +512 MB headroom

    r = subprocess.run(["fallocate", "-l", f"{size_mb}M", str(img)])
    results.append(("fallocate", r.returncode))
    if r.returncode != 0:
        return results

    # 2. Partition: MBR + single primary ext4
    r = subprocess.run([
        "parted", "--script", str(img),
        "mklabel", "msdos",
        "mkpart", "primary", "ext4", "1MiB", "100%",
        "set", "1", "boot", "on",
    ])
    results.append(("parted", r.returncode))
    if r.returncode != 0:
        return results

    # 3. Set up loop device
    lo = subprocess.run(
        ["losetup", "--find", "--show", "--partscan", str(img)],
        capture_output=True, text=True
    )
    results.append(("losetup", lo.returncode))
    if lo.returncode != 0:
        return results

    loop_dev = lo.stdout.strip()
    part_dev = loop_dev + "p1"

    try:
        # 4. Format partition
        r = subprocess.run(["mkfs.ext4", "-F", part_dev])
        results.append(("mkfs.ext4", r.returncode))
        if r.returncode != 0:
            return results

        # 5. Mount and rsync
        mnt = Path(f"/mnt/snapback_{_timestamp()}")
        mnt.mkdir(parents=True, exist_ok=True)

        r = subprocess.run(["mount", part_dev, str(mnt)])
        results.append(("mount", r.returncode))
        if r.returncode != 0:
            return results

        try:
            r = snapshot_os(str(mnt), progress=True)
            results.append(("rsync", r.returncode))

            # 6. Install GRUB
            r = subprocess.run([
                "grub-install",
                "--target=i386-pc",
                f"--boot-directory={mnt}/boot",
                "--recheck",
                loop_dev,
            ])
            results.append(("grub-install", r.returncode))

        finally:
            subprocess.run(["umount", str(mnt)], check=False)
            mnt.rmdir()

    finally:
        subprocess.run(["losetup", "-d", loop_dev], check=False)

    return results


def _estimate_root_mb():
    """Rough estimate of used space under / in MB."""
    r = subprocess.run(
        ["df", "--output=used", "/"],
        capture_output=True, text=True
    )
    lines = r.stdout.strip().splitlines()
    if len(lines) >= 2:
        try:
            return int(lines[1].strip()) // 1024
        except ValueError:
            pass
    return 20_000  # 20 GB fallback
