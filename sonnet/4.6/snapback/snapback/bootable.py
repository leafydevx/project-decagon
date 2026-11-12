"""Clone running OS to a physical disk so it is bootable."""

import subprocess
import shutil
from pathlib import Path
from .snapshot import snapshot_os, _DEFAULT_EXCLUDES


_REQUIRED = ["rsync", "grub-install", "mount", "blkid"]


def clone_to_disk(dest_device, mount_point=None, extra_excludes=None,
                  grub_target="i386-pc", dry_run=False, progress=False):
    """
    Clone the running OS onto dest_device (e.g. /dev/sdb1) and install GRUB.

    dest_device must already be:
      - formatted with a filesystem (ext4 recommended)
      - mounted at mount_point (or we mount it ourselves if mount_point given)

    Steps:
      1. Mount dest_device at mount_point (if not already mounted)
      2. rsync / → mount_point, excluding pseudo-fs
      3. Bind-mount /dev, /proc, /sys into clone and chroot to grub-install
      4. Write /etc/fstab UUID entry for the new root
      5. Unmount everything

    Returns list of (step, returncode).
    """
    for t in _REQUIRED:
        if not shutil.which(t):
            raise RuntimeError(f"{t} not found")

    results = []

    if dry_run:
        print(f"[dry-run] Would clone / → {dest_device} and install GRUB ({grub_target})")
        return results

    mnt = Path(mount_point) if mount_point else Path(f"/mnt/snapback_clone")

    # derive the disk from the partition (strip trailing digit for simple cases)
    disk = _partition_to_disk(dest_device)

    # 1. Mount
    mnt.mkdir(parents=True, exist_ok=True)
    already_mounted = _is_mounted(str(mnt))

    if not already_mounted:
        r = subprocess.run(["mount", dest_device, str(mnt)])
        results.append(("mount", r.returncode))
        if r.returncode != 0:
            return results

    try:
        # 2. rsync
        r = snapshot_os(str(mnt), extra_excludes=extra_excludes,
                        progress=progress)
        results.append(("rsync", r.returncode))
        if r.returncode != 0:
            return results

        # 3. Bind-mounts for chroot
        for pseudo in ("dev", "proc", "sys"):
            src = Path("/") / pseudo
            tgt = mnt / pseudo
            tgt.mkdir(exist_ok=True)
            flag = "--rbind" if pseudo == "dev" else "--bind"
            r = subprocess.run(["mount", flag, str(src), str(tgt)])
            results.append((f"bind-{pseudo}", r.returncode))

        # 4. grub-install inside chroot
        r = subprocess.run([
            "chroot", str(mnt),
            "grub-install",
            f"--target={grub_target}",
            "--recheck",
            disk,
        ])
        results.append(("grub-install", r.returncode))

        # update-grub inside chroot (generates grub.cfg)
        r = subprocess.run(["chroot", str(mnt), "update-grub"])
        results.append(("update-grub", r.returncode))

        # 5. Patch /etc/fstab — replace old root UUID with new one
        new_uuid = _get_uuid(dest_device)
        if new_uuid:
            _patch_fstab(mnt / "etc" / "fstab", new_uuid)
            results.append(("fstab-patch", 0))

    finally:
        # Unmount in reverse order
        for pseudo in ("sys", "proc", "dev"):
            subprocess.run(["umount", "-R", str(mnt / pseudo)], check=False)
        if not already_mounted:
            subprocess.run(["umount", str(mnt)], check=False)

    return results


def _partition_to_disk(dev):
    """
    /dev/sdb1  → /dev/sdb
    /dev/nvme0n1p1 → /dev/nvme0n1
    Falls back to the device unchanged.
    """
    import re
    m = re.match(r"^(/dev/nvme\d+n\d+)p\d+$", dev)
    if m:
        return m.group(1)
    m = re.match(r"^(/dev/[a-z]+)\d+$", dev)
    if m:
        return m.group(1)
    return dev


def _is_mounted(path):
    r = subprocess.run(["mountpoint", "-q", path])
    return r.returncode == 0


def _get_uuid(device):
    r = subprocess.run(
        ["blkid", "-s", "UUID", "-o", "value", device],
        capture_output=True, text=True
    )
    return r.stdout.strip() or None


def _patch_fstab(fstab_path, new_uuid):
    """Replace the / mount UUID in fstab with new_uuid."""
    if not fstab_path.exists():
        return
    lines = fstab_path.read_text().splitlines(keepends=True)
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            out.append(line)
            continue
        parts = stripped.split()
        # fstab: device  mountpoint  fstype  options  dump  pass
        if len(parts) >= 2 and parts[1] == "/":
            # replace whatever the device field is with the new UUID
            out.append(line.replace(parts[0], f"UUID={new_uuid}", 1))
        else:
            out.append(line)
    fstab_path.write_text("".join(out))
