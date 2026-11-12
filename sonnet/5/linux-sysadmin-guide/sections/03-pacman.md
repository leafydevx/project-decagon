# 3. Package Management: pacman

Arch Linux's package manager. Also used by Manjaro, EndeavourOS, and other Arch-based
distros. Fast, simple, and the model most other "all-in-one" package managers imitate.

## Core Syntax

pacman uses single-letter operation flags combined with modifier flags:
`pacman -<operation><modifiers> [target]`

## Everyday Commands

```bash
# Sync package databases + upgrade the whole system (do this together, always)
sudo pacman -Syu

# Install a package
sudo pacman -S firefox

# Install without confirmation prompts (scripts/automation)
sudo pacman -S --noconfirm firefox

# Remove a package
sudo pacman -R firefox

# Remove a package AND its unneeded dependencies
sudo pacman -Rs firefox

# Remove a package, its deps, AND its config files
sudo pacman -Rns firefox

# Search the repos
pacman -Ss keyword

# Search installed packages
pacman -Qs keyword

# Show info about a package (repo)
pacman -Si firefox

# Show info about an installed package
pacman -Qi firefox

# List files owned by a package
pacman -Ql firefox

# Find which package owns a file
pacman -Qo /usr/bin/firefox
```

## Never Do This

```bash
sudo pacman -Sy package-name   # DON'T sync without full upgrade (-u)
```

Partial upgrades (`-Sy` without `-u`) break dependency resolution on a rolling-release
system and are the #1 cause of "my Arch system is broken" reports. Always `-Syu`.

## Cleaning Up

```bash
# Remove orphaned packages (no longer required by anything)
sudo pacman -Qdtq | sudo pacman -Rns -

# Clear the package cache, keeping the last 3 versions of each package
sudo paccache -rk3

# Nuke the entire cache (frees the most space, no rollback cache left)
sudo pacman -Scc
```

## The AUR (Arch User Repository)

pacman only manages official repos. Community-maintained build scripts live in the
AUR and need a helper to build/install:

```bash
# Install an AUR helper (example: yay), build it manually once:
sudo pacman -S --needed git base-devel
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si

# After that, yay wraps pacman and adds AUR support:
yay -S google-chrome
yay -Syu          # upgrades official repos AND AUR packages together
```

**Always read the PKGBUILD** (`cat PKGBUILD` before `makepkg`) for anything from the
AUR — it's unofficial, user-submitted, and runs arbitrary build steps as your user.

## Pacman Hooks and Config

- Config: `/etc/pacman.conf` — enable extra repos (e.g. `[multilib]` for 32-bit
  support) by uncommenting their section.
- Mirror list: `/etc/pacman.d/mirrorlist` — use `reflector` to regenerate it sorted by
  speed: `sudo reflector --latest 20 --sort rate --save /etc/pacman.d/mirrorlist`.
- Downgrading a package after a bad update: packages are cached in
  `/var/cache/pacman/pkg/` — `sudo pacman -U /var/cache/pacman/pkg/pkgname-oldver.pkg.tar.zst`.

## Quick Reference

| Task | Command |
|---|---|
| Full system upgrade | `sudo pacman -Syu` |
| Install | `sudo pacman -S <pkg>` |
| Remove + deps | `sudo pacman -Rs <pkg>` |
| Search repo | `pacman -Ss <term>` |
| List installed | `pacman -Q` |
| Orphans | `pacman -Qdtq` |
| What owns this file | `pacman -Qo <path>` |
| Clear old cache | `sudo paccache -rk3` |
