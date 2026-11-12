# 4. Package Management: apt

Debian/Ubuntu's package manager (a frontend over the lower-level `dpkg`). `apt` is the
modern command; you'll still see `apt-get`/`apt-cache` in older scripts — `apt` is
preferred for interactive use.

## Everyday Commands

```bash
# Refresh package index (always run before install/upgrade)
sudo apt update

# Upgrade installed packages
sudo apt upgrade

# Upgrade and allow removing/installing packages to resolve deps (kernel upgrades etc.)
sudo apt full-upgrade

# Install a package
sudo apt install nginx

# Install without prompts (automation)
sudo apt install -y nginx

# Remove a package, keep config files
sudo apt remove nginx

# Remove a package AND its config files
sudo apt purge nginx

# Remove unneeded auto-installed dependencies
sudo apt autoremove

# Search for a package
apt search keyword

# Show package details
apt show nginx

# List installed packages
apt list --installed

# List upgradable packages
apt list --upgradable
```

## Cleaning Up

```bash
sudo apt autoremove        # removes orphaned auto-installed deps
sudo apt clean             # clears the downloaded .deb cache entirely
sudo apt autoclean         # clears only outdated .deb files from cache
```

## Holding a Package Back (don't auto-upgrade it)

```bash
sudo apt-mark hold nginx
sudo apt-mark unhold nginx
apt-mark showhold
```

## dpkg: The Layer Underneath

`apt` resolves dependencies and fetches from repos; `dpkg` installs the actual `.deb`
files. You'll use `dpkg` directly for local files or to query file ownership:

```bash
sudo dpkg -i package.deb      # install a local .deb (then: sudo apt install -f to fix deps)
dpkg -L nginx                 # list files owned by a package
dpkg -S /usr/sbin/nginx       # find which package owns a file
dpkg -l | grep nginx          # list installed packages matching a pattern
```

## PPAs (Ubuntu) and Third-Party Repos

```bash
sudo add-apt-repository ppa:someone/their-ppa
sudo apt update
sudo apt install package-from-ppa

# Remove it later:
sudo add-apt-repository --remove ppa:someone/their-ppa
```

**Only add PPAs from sources you trust** — they run with full package-install
privileges on your system.

## Fixing a Broken apt State

```bash
sudo apt --fix-broken install     # repairs unmet dependencies
sudo dpkg --configure -a          # finishes interrupted package configuration
sudo rm /var/lib/apt/lists/lock   # ONLY if apt is hung and no apt process is running
```

## Quick Reference

| Task | Command |
|---|---|
| Refresh index | `sudo apt update` |
| Upgrade all | `sudo apt upgrade` |
| Full upgrade (deps may change) | `sudo apt full-upgrade` |
| Install | `sudo apt install <pkg>` |
| Purge (+ configs) | `sudo apt purge <pkg>` |
| Remove orphans | `sudo apt autoremove` |
| Search | `apt search <term>` |
| What owns this file | `dpkg -S <path>` |
| Hold a version | `sudo apt-mark hold <pkg>` |
