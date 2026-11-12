# 12. Backups & Recovery

A backup that's never been restored is a hope, not a backup. Test restores periodically.

## rsync — The Workhorse

```bash
# Local or remote sync, preserving permissions/times, compressed in transit
rsync -avz /source/dir/ /backup/dir/
rsync -avz /source/dir/ user@remote:/backup/dir/

# Mirror exactly, deleting files in dest that no longer exist in source (careful!)
rsync -avz --delete /source/dir/ /backup/dir/

# Dry run first — always, before using --delete
rsync -avzn --delete /source/dir/ /backup/dir/
```

**Trailing slash matters**: `/source/dir/` copies the *contents* of `dir` into the
destination; `/source/dir` (no slash) copies `dir` itself as a subdirectory. This trips
up almost everyone at least once.

## tar — Archiving

```bash
tar -czvf backup.tar.gz /path/to/dir      # create, gzip-compressed
tar -xzvf backup.tar.gz -C /restore/path   # extract
tar -tzvf backup.tar.gz                     # list contents without extracting
tar -czvf backup.tar.gz --exclude='node_modules' /path/to/dir   # exclude patterns
```

## Automating Backups with a systemd Timer

See Section 7 for the timer pattern. Pair it with a backup script:

```bash
#!/bin/bash
# /opt/scripts/backup.sh
set -euo pipefail
DEST="/backup/$(date +%F)"
mkdir -p "$DEST"
rsync -a /etc "$DEST/etc"
rsync -a /home "$DEST/home"
find /backup -maxdepth 1 -mtime +30 -exec rm -rf {} \;   # prune backups older than 30 days
```

## Database Dumps (don't just copy the data files live)

```bash
# PostgreSQL
pg_dump dbname > dbname-$(date +%F).sql
pg_dumpall > all-databases-$(date +%F).sql

# MySQL/MariaDB
mysqldump dbname > dbname-$(date +%F).sql
mysqldump --all-databases > all-databases-$(date +%F).sql
```

## Disk Imaging (full-disk or partition backup)

```bash
sudo dd if=/dev/sda of=/backup/disk.img bs=4M status=progress
# restore:
sudo dd if=/backup/disk.img of=/dev/sda bs=4M status=progress
```

Use `dd` for full-disk clones/recovery scenarios — it's slow and copies every byte
including free space, so prefer filesystem-level tools (`rsync`, `tar`, or
snapshot-based backup) for routine backups.

## Btrfs/LVM Snapshots for Fast, Space-Efficient Backups

See Section 9 — snapshots are near-instant and only store the *differences*, but they
live on the same disk by default. **A snapshot is not a backup** unless it's also
copied to separate physical storage (another disk, another machine, or the cloud).

## Off-Site / Cloud Backup Tools

```bash
# restic — encrypted, deduplicated, works with local/S3/B2/SFTP backends
restic init --repo /backup/restic-repo
restic -r /backup/restic-repo backup /home
restic -r /backup/restic-repo snapshots
restic -r /backup/restic-repo restore latest --target /restore

# borgbackup — similar feature set, very mature
borg init --encryption=repokey /backup/borg-repo
borg create /backup/borg-repo::$(date +%F) /home
borg list /backup/borg-repo
```

## The 3-2-1 Rule

- **3** copies of your data
- **2** different storage media/types
- **1** copy off-site (different building, or cloud)

## Recovery Drills

Schedule an actual test restore (to a scratch VM or spare disk) at least quarterly.
A backup strategy that's never been exercised end-to-end is unverified — you find out
whether it actually works at the worst possible time otherwise.
