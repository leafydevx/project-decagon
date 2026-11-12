# secaudit

Read-only Linux security checks. Makes no changes to your system.

Checks: SSH root login / password auth / empty passwords, extra UID 0 accounts,
permissions on `/etc/shadow`, `/etc/passwd`, `/etc/sudoers`.

```bash
python -m secaudit       # exits 1 if any check FAILs
sudo python -m secaudit  # root can read files unprivileged users cannot
```

Tests: `python -m unittest discover -s tests`
