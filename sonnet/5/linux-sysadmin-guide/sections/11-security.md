# 11. Security Hardening

## SSH

```
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no      # key-only auth, after confirming key login works
Protocol 2
MaxAuthTries 3
AllowUsers alice bob            # explicit allowlist, optional but strong
```

```bash
sudo systemctl restart sshd
```

Test key login in a **second session** before closing the one you used to edit the
config — a mistake here can lock you out of a remote box.

## Fail2ban — Auto-ban Brute-Force Attempts

```bash
sudo apt install fail2ban    # or: sudo dnf install fail2ban / sudo pacman -S fail2ban
sudo systemctl enable --now fail2ban

sudo fail2ban-client status sshd        # see current bans for the sshd jail
sudo fail2ban-client set sshd unbanip 1.2.3.4   # manually unban an IP
```

`/etc/fail2ban/jail.local`:

```ini
[sshd]
enabled = true
maxretry = 5
bantime = 1h
```

## Firewall: Default-Deny

Only open what you need. See Section 8 for `ufw`/`firewalld` syntax. The pattern:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Keeping Software Updated

```bash
sudo apt update && sudo apt upgrade -y     # Debian/Ubuntu
sudo dnf upgrade --refresh                  # Fedora/RHEL
sudo pacman -Syu                             # Arch
```

Set up automation (Section 2) for servers — unpatched software is the most common
real-world attack vector, more than any exotic exploit.

## Finding Risky Permissions

```bash
# World-writable files (anyone can modify)
find / -xdev -type f -perm -0002 2>/dev/null

# setuid/setgid binaries (run with elevated privilege — audit this list)
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null

# Files with no owner (orphaned, often from a removed user)
find / -xdev \( -nouser -o -nogroup \) 2>/dev/null
```

## Checking for Listening Services You Didn't Expect

```bash
sudo ss -tulpn
```

Anything listening that you can't account for deserves investigation — check which
process/package it belongs to and whether it should be running at all.

## Auditing Logins

```bash
last                  # recent login history
lastb                  # recent FAILED login attempts (needs sudo on some systems)
who                     # who's logged in right now
w                        # who's logged in + what they're doing
journalctl -u sshd | grep -i "accepted\|failed"
```

## SELinux (Fedora/RHEL) / AppArmor (Debian/Ubuntu)

Mandatory access control — don't disable it to "fix" a permission problem; figure out
the right policy instead.

```bash
# SELinux
getenforce                       # Enforcing / Permissive / Disabled
sudo setenforce 0                # TEMPORARY permissive, for debugging ONLY
sudo ausearch -m avc -ts recent   # see what SELinux has been blocking
sudo semanage port -l | grep http # check what ports a policy allows

# AppArmor
sudo aa-status                    # show loaded profiles and their mode
sudo aa-complain /path/to/profile  # set a profile to complain (log, don't block) for debugging
```

## Checking for Rootkits / Unexpected Changes

```bash
sudo rkhunter --check          # install rkhunter first; scans for known rootkit signatures
sudo debsums -c                 # Debian/Ubuntu: verify installed files match package checksums
rpm -Va                          # RHEL/Fedora: verify installed files against package database
```

## Minimal Attack Surface Checklist

- [ ] Root login over SSH disabled
- [ ] Password SSH auth disabled (keys only)
- [ ] Firewall default-deny, only required ports open
- [ ] fail2ban or equivalent running on anything internet-facing
- [ ] Automatic security updates enabled (servers)
- [ ] No unused services listening (`ss -tulpn` reviewed)
- [ ] SELinux/AppArmor enforcing, not disabled
- [ ] Regular, tested backups (see Section 12)
