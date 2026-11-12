# 9. Storage & Filesystems

## Viewing Disks and Partitions

```bash
lsblk                     # tree view of block devices and mount points
lsblk -f                   # same, plus filesystem type and UUID
df -h                       # disk usage by mounted filesystem, human-readable
du -sh /path/*               # size of each item in a directory
du -sh /path | sort -rh      # (combine with sort to find the biggest directories)
sudo fdisk -l                # list disks and partition tables (MBR/GPT detail)
blkid                        # UUIDs and filesystem types of all block devices
```

## Finding What's Eating Disk Space

```bash
sudo du -ahx / | sort -rh | head -20    # biggest files/dirs on the root filesystem
ncdu /                                   # interactive, much faster to browse (install first)
sudo journalctl --disk-usage             # check if systemd logs are the culprit
```

## Partitioning and Formatting

```bash
sudo fdisk /dev/sdb         # interactive partitioning (classic, MBR or GPT)
sudo parted /dev/sdb         # alternative, better GPT support, scriptable

sudo mkfs.ext4 /dev/sdb1
sudo mkfs.xfs /dev/sdb1
sudo mkfs.btrfs /dev/sdb1
```

**Double-check the device name before formatting** — `mkfs` on the wrong device is
irreversible data loss. `lsblk` first, always.

## Mounting

```bash
sudo mount /dev/sdb1 /mnt/data
sudo umount /mnt/data

mount | grep sdb1        # confirm it's mounted and where
```

### Persistent mounts via `/etc/fstab`

```bash
blkid /dev/sdb1    # get the UUID first — use UUIDs, not /dev/sdX names (those can shift)
```

```
UUID=1234-5678  /mnt/data  ext4  defaults  0  2
```

```bash
sudo mount -a       # test the fstab entry without rebooting
findmnt /mnt/data   # verify it mounted as expected
```

## LVM (Logical Volume Manager) — Resizable Storage

```bash
sudo pvcreate /dev/sdb              # mark a disk as an LVM physical volume
sudo vgcreate vg_data /dev/sdb       # create a volume group
sudo lvcreate -L 50G -n lv_app vg_data   # create a logical volume
sudo mkfs.ext4 /dev/vg_data/lv_app

# Growing a volume later (while in use, online resize):
sudo lvextend -L +20G /dev/vg_data/lv_app
sudo resize2fs /dev/vg_data/lv_app       # for ext4
sudo xfs_growfs /mnt/data                 # for xfs (mount point, not device)

pvs    # list physical volumes
vgs    # list volume groups
lvs    # list logical volumes
```

## Btrfs Snapshots (Fedora/openSUSE default, Arch optional)

```bash
sudo btrfs subvolume create /mnt/@snapshots
sudo btrfs subvolume snapshot /mnt/@ /mnt/@snapshots/backup-$(date +%F)
sudo btrfs subvolume list /mnt
sudo btrfs subvolume delete /mnt/@snapshots/backup-2026-01-01
```

## Swap

```bash
free -h                      # check current swap usage
swapon --show                 # list active swap devices/files
sudo swapon /swapfile          # activate
sudo swapoff /swapfile         # deactivate (frees it for editing/deletion)
cat /proc/sys/vm/swappiness    # how aggressively the kernel swaps (0-100, lower = less eager)
sudo sysctl vm.swappiness=10   # temporary change; add to /etc/sysctl.conf to persist
```

## Checking Filesystem Health

```bash
sudo fsck /dev/sdb1          # NEVER run on a mounted filesystem — unmount first
sudo smartctl -a /dev/sda     # drive health (SMART data) — install smartmontools first
sudo smartctl -H /dev/sda     # quick pass/fail health summary
```
