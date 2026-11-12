# sysmon

A tiny, dependency-free Linux system monitor. Reads `/proc` directly.

## Usage

```bash
python -m sysmon              # one-shot summary
python -m sysmon --watch 2    # refresh every 2s (Ctrl+C to quit)
python -m sysmon --json       # machine-readable snapshot
python -m sysmon --top 10     # show 10 processes by memory
```

## Tests

```bash
python -m unittest discover -s tests
```
