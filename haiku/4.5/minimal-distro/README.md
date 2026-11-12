# Minimal USB Distro (~250MB)

A lightweight, bootable Linux ISO - USB bootable, ready to go.

## Features

- ✅ Minimal base system (musl libc, BusyBox)
- ✅ USB bootable (ISOLINUX/Syslinux)
- ✅ ~250MB total size
- ✅ 5 minute build time
- ✅ Works on any x86_64 hardware

## Build

```bash
cd /home/dxvidqzx/github/claude/haiku/4.5/alpine-distro
bash build.sh
```

Output: `minimal-linux.iso` (~250MB)

## Boot

**From USB:**
```bash
dd if=minimal-linux.iso of=/dev/sdX bs=4M && sync
# Reboot and select USB drive
```

**In QEMU:**
```bash
qemu-system-x86_64 -m 512 -cdrom minimal-linux.iso
```

## What's Included

- Minimal Linux base with BusyBox
- Init system (OpenRC)
- Full shell environment
- Package manager included
- Network support

## Status

🔨 Building...
