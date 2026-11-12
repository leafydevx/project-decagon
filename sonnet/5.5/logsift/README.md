# logsift

Summarize syslog-style and nginx/Apache access logs: log levels, status codes,
top IPs and paths, noisiest processes, and failed SSH logins per IP.

```bash
python -m logsift /var/log/nginx/access.log
python -m logsift auth.log syslog --top 10
journalctl -n 500 --no-pager | python -m logsift
```

Tests: `python -m unittest discover -s tests`
