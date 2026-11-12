# 10. Monitoring & Troubleshooting

## CPU and Memory, Live

```bash
htop            # interactive, color, per-core — install first if missing
top             # always available, no dependencies
vmstat 1         # system-wide CPU/memory/IO snapshot every 1s
free -h          # memory + swap summary
nproc            # number of CPU cores available
lscpu            # detailed CPU info (model, cores, cache, flags)
```

## Finding What's Using Resources

```bash
ps aux --sort=-%cpu | head -10     # top 10 processes by CPU
ps aux --sort=-%mem | head -10     # top 10 processes by memory
pidof nginx                         # get PID(s) of a process by name
pgrep -f "python.*worker"           # search process list by pattern

# Per-process IO:
sudo iotop                          # live disk IO by process (install first)
```

## Disk IO and Throughput

```bash
iostat -x 1          # per-device IO stats every second (from sysstat package)
sudo dd if=/dev/zero of=/tmp/test bs=1M count=1024 oflag=direct   # rough write speed test
sudo hdparm -t /dev/sda   # rough read speed test
```

## Network Throughput and Connections

```bash
sudo iftop                # live bandwidth usage per connection
sudo nethogs               # live bandwidth usage per process
ss -s                       # summary of socket statistics
```

## Killing Stuck Processes

```bash
kill -15 <pid>       # SIGTERM — ask nicely, let it clean up (always try this first)
kill -9 <pid>         # SIGKILL — force kill, no cleanup (last resort)
pkill -f "process name"
killall processname
```

## Checking System Logs for Problems

```bash
journalctl -p err -b         # errors since boot
journalctl -k                 # kernel messages only (dmesg equivalent via journal)
dmesg -T | tail -50            # kernel ring buffer, human-readable timestamps
dmesg -T | grep -i error
cat /var/log/syslog | tail -50     # Debian/Ubuntu non-systemd-journal logs
```

## Boot Problems

```bash
systemctl --failed              # units that failed during boot
journalctl -b -1 -p err          # errors from the PREVIOUS boot (if it crashed)
systemd-analyze blame             # slow-starting services
```

If the system won't boot at all: boot into recovery/rescue mode from GRUB, or a live
USB, then `chroot` into the installed system to investigate/repair.

## Out of Disk Space Emergencies

```bash
df -h                                    # confirm which filesystem is full
sudo du -ahx / | sort -rh | head -20     # find the biggest offenders fast
sudo journalctl --vacuum-size=200M        # logs are a common silent culprit
sudo apt clean  /  sudo pacman -Scc  /  sudo dnf clean all   # package cache, often large
```

## Load Average, Explained

```bash
uptime
```

Three numbers = load average over 1, 5, 15 minutes. Compare against `nproc` — a load
of 4.0 on a 4-core machine means the CPUs are fully busy; on an 8-core machine it means
50% headroom. Sustained load well above core count = CPU-bound bottleneck; investigate
with `htop`/`ps aux --sort=-%cpu`.

## A Basic Troubleshooting Checklist

1. `journalctl -p err -b` — anything obviously broken logged recently?
2. `systemctl --failed` — any failed units?
3. `df -h` / `free -h` — out of disk or memory?
4. `ss -tulpn` — is the service actually listening on the expected port?
5. `curl -v localhost:PORT` — does it respond locally (rules out firewall/network)?
6. Check the application's own logs (often under `/var/log/<app>/` or via `journalctl -u <app>`).
