# 2. First Hour on a New System

A checklist for right after install, before you start real work.

## 1. Update Everything

```bash
# Arch/Manjaro
sudo pacman -Syu

# Debian/Ubuntu
sudo apt update && sudo apt upgrade -y

# Fedora/RHEL
sudo dnf upgrade --refresh
```

## 2. Create a Non-Root User (if you installed as root)

```bash
useradd -m -G wheel -s /bin/bash yourname   # Arch/Fedora (wheel group)
useradd -m -G sudo -s /bin/bash yourname    # Debian/Ubuntu (sudo group)
passwd yourname
```

Then grant sudo. On Arch/Fedora, uncomment the `%wheel ALL=(ALL:ALL) ALL` line in
`visudo`. On Debian/Ubuntu, being in the `sudo` group is already enough.

```bash
sudo visudo   # always edit sudoers with visudo, never a text editor directly
```

## 3. Set Hostname and Timezone

```bash
sudo hostnamectl set-hostname myhost
sudo timedatectl set-timezone Region/City   # e.g. America/New_York
timedatectl status   # verify
```

## 4. Configure the Firewall

```bash
# Arch/Debian/Ubuntu — ufw (simplest)
sudo apt install ufw        # or: sudo pacman -S ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable

# Fedora/RHEL — firewalld (installed by default)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## 5. Harden SSH (if the box is reachable from the network)

Edit `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no      # once you've copied your SSH key over
```

```bash
sudo systemctl restart sshd
```

Copy your key first with `ssh-copy-id user@host` — test that key login works in a
**second terminal** before you close the session you're hardening, so you don't lock
yourself out.

## 6. Enable Automatic Security Updates (servers)

```bash
# Debian/Ubuntu
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades

# Fedora/RHEL
sudo dnf install dnf-automatic
sudo systemctl enable --now dnf-automatic.timer
```

Arch has no equivalent by design — rolling release means you're expected to update
manually and read the Arch news feed (`archlinux.org/news`) before big upgrades.

## 7. Install Core Tooling

```bash
# Arch
sudo pacman -S base-devel git vim htop tmux rsync

# Debian/Ubuntu
sudo apt install build-essential git vim htop tmux rsync

# Fedora
sudo dnf groupinstall "Development Tools"
sudo dnf install git vim htop tmux rsync
```

## 8. Check Disk Layout and Free Space

```bash
lsblk -f
df -h
```

## 9. Set Up Swap (if not already present)

```bash
free -h   # check if swap exists
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 10. Reboot and Verify

```bash
sudo reboot
# after reboot:
uname -a
systemctl --failed   # should be empty
```
