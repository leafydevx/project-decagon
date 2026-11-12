# 6. Users, Groups & Permissions

## User Management

```bash
sudo useradd -m -G wheel -s /bin/bash alice   # -m creates home dir, -G adds to group
sudo passwd alice                              # set/change password
sudo usermod -aG docker alice                  # add to an additional group (-a = append!)
sudo userdel -r alice                          # delete user AND home directory
```

**`-a` matters on `usermod -G`** — without it, `-G` *replaces* the user's group list
instead of appending to it, silently dropping them from every other group.

## Switching Users / Privilege Escalation

```bash
sudo command              # run one command as root
sudo -i                   # root login shell (loads root's environment)
sudo -u alice command     # run a command as another user
su - alice                # switch to alice, loading her environment (needs her password)
```

Prefer `sudo` over `su` on modern systems — it's logged per-command in
`/var/log/auth.log` (Debian) or `journalctl -u sudo` (systemd), and you don't share the
root password.

## File Permissions

```
-rwxr-xr--  1 alice developers  4096 Jan 1 12:00 script.sh
 │││││││││
 │││└┴┴──── other: r--  (read only)
 │└┴┴────── group: r-x  (read + execute)
 └┴┴─────── owner: rwx  (read + write + execute)
```

```bash
chmod 755 script.sh        # rwxr-xr-x — common for executables/scripts
chmod 644 file.txt         # rw-r--r-- — common for regular files
chmod u+x script.sh        # add execute for owner only
chmod -R g+w /shared/dir   # recursively add group write

chown alice:developers file.txt    # change owner and group
chown -R alice:developers /home/alice   # recursively
```

## Numeric Permission Reference

| Number | Permission |
|---|---|
| 7 | rwx |
| 6 | rw- |
| 5 | r-x |
| 4 | r-- |
| 0 | --- |

Common combos: `644` (files), `755` (executables/dirs), `600` (private files, e.g.
SSH keys), `700` (private dirs, e.g. `~/.ssh`).

## Special Permission Bits

```bash
chmod u+s /path/to/binary   # setuid — runs as the file's owner, not the caller
chmod g+s /path/to/dir      # setgid on a dir — new files inherit the dir's group
chmod +t /tmp                # sticky bit — only the file owner can delete their own files
```

## sudo Configuration

**Always edit with `visudo`** — it validates syntax before saving, preventing you from
locking yourself out with a typo.

```bash
sudo visudo
```

```
# Grant passwordless sudo to a specific user (use sparingly, e.g. for automation):
alice ALL=(ALL) NOPASSWD: ALL

# Grant a group sudo for everything (default on Arch/Fedora via wheel):
%wheel ALL=(ALL:ALL) ALL

# Grant sudo for only specific commands:
alice ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx
```

## Finding Permission Problems

```bash
namei -l /path/to/file          # show permissions of every path component
find /path -perm -o+w            # find world-writable files (potential security issue)
find /path -nouser -o -nogroup   # find files owned by deleted users/groups
```
