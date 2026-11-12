# 7. systemd: Services & Logs

systemd is the init system and service manager on virtually every modern distro
(Arch, Debian/Ubuntu, Fedora/RHEL, openSUSE). Alpine is the main holdout, using OpenRC.

## Managing Services

```bash
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx          # re-read config without dropping connections (if supported)
sudo systemctl enable nginx          # start automatically on boot
sudo systemctl disable nginx
sudo systemctl enable --now nginx    # enable AND start in one command

systemctl status nginx               # current state + recent log lines
systemctl is-active nginx
systemctl is-enabled nginx
```

## Checking Overall System Health

```bash
systemctl --failed          # list units that failed to start — check this after any boot issue
systemctl list-units --type=service --state=running
systemd-analyze blame        # which services took the longest to start at boot
systemd-analyze critical-chain   # the critical path of the boot sequence
```

## Reading Logs with journalctl

```bash
journalctl -u nginx              # all logs for one unit
journalctl -u nginx -f            # follow (like tail -f)
journalctl -u nginx --since today
journalctl -u nginx --since "1 hour ago"
journalctl -p err                 # only error-level and above, across everything
journalctl -b                     # logs since the current boot
journalctl -b -1                  # logs from the previous boot (useful after a crash)
journalctl --disk-usage           # how much space the journal is using
sudo journalctl --vacuum-time=2weeks   # delete logs older than 2 weeks
sudo journalctl --vacuum-size=500M     # cap total journal size
```

## Writing a Custom systemd Service

`/etc/systemd/system/myapp.service`:

```ini
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=myapp
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/run.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload       # required after creating/editing a unit file
sudo systemctl enable --now myapp
```

## Timers (systemd's cron replacement)

`/etc/systemd/system/backup.timer`:

```ini
[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Pairs with a matching `backup.service` (same name, no `[Timer]` section needed there).

```bash
sudo systemctl enable --now backup.timer
systemctl list-timers              # see all active timers and next run time
```

## Targets (systemd's "runlevels")

```bash
systemctl get-default                       # see current default target
sudo systemctl set-default multi-user.target # boot to CLI, no GUI
sudo systemctl set-default graphical.target  # boot to GUI
systemctl isolate rescue.target              # drop to single-user/rescue mode NOW (careful)
```

## Resource Limits on a Service (cgroups, built in)

Add to a service's `[Service]` section:

```ini
MemoryMax=512M
CPUQuota=50%
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart myapp
systemd-cgtop   # live resource usage per cgroup/service
```
