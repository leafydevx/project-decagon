# portwatch

Lists listening TCP sockets (IPv4 and IPv6) with the owning process, and flags
whether each is reachable from other machines or localhost only. Parses `/proc/net/tcp*`.

```bash
python -m portwatch
sudo python -m portwatch   # see processes owned by other users
```

Tests: `python -m unittest discover -s tests`
