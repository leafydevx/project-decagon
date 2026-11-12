# 5. Package Management: dnf

Fedora/RHEL/Rocky/AlmaLinux's package manager — the successor to `yum` (yum commands
still mostly work as aliases on these systems, but `dnf` is current).

## Everyday Commands

```bash
# Upgrade everything (dnf combines "refresh metadata" + "upgrade" in one step)
sudo dnf upgrade --refresh

# Install a package
sudo dnf install httpd

# Install without prompts
sudo dnf install -y httpd

# Remove a package
sudo dnf remove httpd

# Search for a package
dnf search keyword

# Show package details
dnf info httpd

# List installed packages
dnf list installed

# List available updates
dnf list updates

# Find which package provides a file/command
dnf provides */ifconfig
```

## Package Groups

RHEL-family distros bundle related packages into groups (similar to Debian "tasks"):

```bash
dnf group list
sudo dnf groupinstall "Development Tools"
sudo dnf groupremove "Development Tools"
```

## Cleaning Up

```bash
sudo dnf autoremove          # removes orphaned dependencies
sudo dnf clean all           # clears all cached metadata and packages
sudo dnf clean packages      # clears only cached .rpm files
```

## History and Rollback

dnf tracks every transaction — one of its best features over apt/pacman:

```bash
dnf history                       # list past transactions
dnf history info 42               # details of transaction #42
sudo dnf history undo 42          # reverse transaction #42
sudo dnf history rollback 42      # roll the system back to the state after #42
```

## Repos and EPEL

RHEL-clones (Rocky/Alma) ship a minimal set of repos by default. EPEL ("Extra
Packages for Enterprise Linux") adds a huge amount of commonly needed software:

```bash
sudo dnf install epel-release
sudo dnf upgrade --refresh
```

```bash
dnf repolist                       # show enabled repos
sudo dnf config-manager --set-enabled crb   # enable CodeReady/PowerTools (needed by some EPEL pkgs)
```

## Downgrading a Package

```bash
dnf list --showduplicates httpd    # see available versions
sudo dnf downgrade httpd
```

## Quick Reference

| Task | Command |
|---|---|
| Upgrade all | `sudo dnf upgrade --refresh` |
| Install | `sudo dnf install <pkg>` |
| Remove | `sudo dnf remove <pkg>` |
| Search | `dnf search <term>` |
| What provides a file | `dnf provides <path>` |
| List transactions | `dnf history` |
| Undo a transaction | `sudo dnf history undo <id>` |
| Install a group | `sudo dnf groupinstall "<name>"` |
