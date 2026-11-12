# 13. Command Cheat Sheet

One page, grouped by task. Ctrl+F this file.

## Package Management

| Task | pacman (Arch) | apt (Debian/Ubuntu) | dnf (Fedora/RHEL) |
|---|---|---|---|
| Upgrade all | `sudo pacman -Syu` | `sudo apt update && sudo apt upgrade` | `sudo dnf upgrade --refresh` |
| Install | `sudo pacman -S pkg` | `sudo apt install pkg` | `sudo dnf install pkg` |
| Remove | `sudo pacman -Rs pkg` | `sudo apt remove pkg` | `sudo dnf remove pkg` |
| Purge/configs too | `sudo pacman -Rns pkg` | `sudo apt purge pkg` | n/a |
| Search | `pacman -Ss term` | `apt search term` | `dnf search term` |
| Package info | `pacman -Si pkg` | `apt show pkg` | `dnf info pkg` |
| List installed | `pacman -Q` | `dpkg -l` | `dnf list installed` |
| What owns file | `pacman -Qo path` | `dpkg -S path` | `dnf provides path` |
| Remove orphans | `pacman -Qdtq \| pacman -Rns -` | `sudo apt autoremove` | `sudo dnf autoremove` |
| Clean cache | `sudo paccache -rk3` | `sudo apt clean` | `sudo dnf clean all` |

## Users & Permissions

```bash
sudo useradd -m -G wheel -s /bin/bash alice   # create user
sudo passwd alice                              # set password
sudo usermod -aG docker alice                   # add to group (-a = append, don't forget!)
chmod 755 file      # rwxr-xr-x
chmod 644 file       # rw-r--r--
chown user:group file
sudo visudo           # edit sudoers safely
```

## systemd / Services

```bash
sudo systemctl enable --now nginx    # enable + start
sudo systemctl restart nginx
systemctl status nginx
systemctl --failed                    # failed units
journalctl -u nginx -f                 # follow logs
journalctl -p err -b                    # errors since boot
sudo systemctl daemon-reload            # after editing a unit file
```

## Networking

```bash
ip a                        # addresses
ip r                         # routes
ss -tulpn                     # listening ports + owning process
curl -I https://host           # quick HTTP check
dig +short host                 # DNS lookup
ssh-copy-id user@host            # push SSH key
sudo ufw allow 443/tcp            # open a port (ufw)
sudo firewall-cmd --add-port=443/tcp --permanent --zone=public   # (firewalld)
```

## Storage

```bash
lsblk -f                 # disks + filesystems + mount points
df -h                      # disk usage by filesystem
du -sh * | sort -rh         # biggest items in current dir
sudo mount /dev/sdb1 /mnt    # mount
blkid                        # get UUIDs for /etc/fstab
sudo mount -a                 # test fstab without reboot
```

## Monitoring / Troubleshooting

```bash
htop                              # live CPU/mem
ps aux --sort=-%mem | head         # top memory consumers
free -h                             # memory + swap
uptime                               # load average
sudo ss -tulpn                        # listening ports
journalctl -p err -b                   # recent errors
dmesg -T | tail -50                     # kernel messages
kill -15 PID                             # graceful stop
kill -9 PID                               # force kill
```

## Security Quick Checks

```bash
sudo ufw status verbose                 # firewall rules
sudo fail2ban-client status sshd         # banned IPs
getenforce                                # SELinux mode
sudo aa-status                             # AppArmor profiles
last                                        # recent logins
lastb                                        # recent failed logins
```

## Backup One-Liners

```bash
rsync -avz /src/ /dst/                    # sync (note trailing slashes!)
tar -czvf backup.tar.gz /path               # archive
pg_dump dbname > dump.sql                    # Postgres dump
mysqldump dbname > dump.sql                   # MySQL/MariaDB dump
```

## "Something's Broken" First Steps

```bash
journalctl -p err -b        # 1. recent errors
systemctl --failed           # 2. failed services
df -h && free -h              # 3. disk/memory full?
sudo ss -tulpn                # 4. is it actually listening?
curl -v localhost:PORT          # 5. does it respond locally?
```
