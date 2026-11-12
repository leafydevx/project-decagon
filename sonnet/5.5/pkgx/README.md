# pkgx

One command for every distro's package manager (pacman, apt, dnf, zypper, apk).
Detects your distro from `/etc/os-release`.

```bash
python -m pkgx install vim        # runs the right command, adds sudo if needed
python -m pkgx search ripgrep
python -m pkgx update -y
python -m pkgx install vim -n     # dry run: just print the command
python -m pkgx info curl --manager apt   # force a specific manager
```

Tests: `python -m unittest discover -s tests`
