# Claude Model Guide

## Quick Reference by Use Case

### 🚀 Speed-Critical Tasks
- **Best:** `haiku/5.5` — ultra-fast, low cost ($0.10/$0.50 per MTok)
- **Use for:** Classifications, summaries, simple Q&A, high-volume processing

### ⚡ Balanced Performance (Recommended for Most)
- **Best:** `sonnet/5.5` — speed + capability ($2/$10 per MTok)
- **Use for:** General coding, agent work, everyday tasks, chat
- **When to pick older:** `sonnet/5` for compatibility, `sonnet/4.6` for legacy systems

### 🧠 Complex Reasoning & Long-Horizon Tasks
- **Best:** `opus/5.5` — powerful reasoning ($4/$20 per MTok)
- **Use for:** Hard problems, multi-step workflows, advanced analysis
- **When to pick older:** `opus/5` for thinking budget support, `opus/4.8/4.7` for specific API features

### 🔥 Maximum Capability (Most Complex)
- **Best:** `fable/5.1` — state-of-the-art reasoning ($10/$50 per MTok)
- **Use for:** Autonomous agents, long-horizon tasks, frontier difficulty problems
- **When to pick:** Only when Opus isn't enough

## Model Features by Version

| Model | Context | Thinking | Cost (in/$out) | Speed | Best For |
|---|---|---|---|---|---|
| Haiku 5.5 | 1M | Adaptive | $0.10/$0.50 | ⚡⚡⚡ | High-volume, latency-critical |
| Sonnet 5.5 | 1M | Adaptive | $2/$10 | ⚡⚡ | General coding & agents |
| Opus 5.5 | 1M | Adaptive* | $4/$20 | ⚡ | Complex reasoning |
| Fable 5.1 | 1M | Always-on | $10/$50 | 🐢 | Hardest problems, autonomy |

*Opus 5.5: thinking is always on, can't be disabled (use effort levels instead)

## File Organization

Create your projects like this:

```bash
cd ~/github/claude/sonnet/5.5
mkdir my-project
cd my-project
claude init  # Initialize as a Claude project
```

Each model folder is independent - organize by the model you're testing with!

## Model Comparison

### Thinking
- **Fable 5.1:** Always on (adaptive), can't disable
- **Opus 5.5:** Always on (adaptive), can't disable, default `medium` effort
- **Opus 5:** Always on by default (adaptive), can disable at `low-high` effort
- **Sonnet 5.5:** Adaptive by default, can use `between_tools` mode
- **Haiku 5.5:** Adaptive by default, can disable at `low-high` effort
- **Haiku/Sonnet/Opus 4.x:** Budget-based thinking (deprecated pattern)

### Token Limits
- **Max Output:** 128K (Fable, Opus 5.5+, Sonnet 5.5, Sonnet 5)
- **Context Window:** 1M (all current models except Haiku 4.5 which is 200K)

### Capabilities Matrix

| Feature | Haiku | Sonnet | Opus | Fable |
|---|---|---|---|---|
| Coding | ✓ | ✓✓ | ✓✓✓ | ✓✓✓ |
| Reasoning | ✓ | ✓✓ | ✓✓✓ | ✓✓✓✓ |
| Long context | ✓ (1M) | ✓ (1M) | ✓ (1M) | ✓ (1M) |
| Agents | ✓ | ✓✓ | ✓✓✓ | ✓✓✓✓ |
| Cost efficient | ✓✓✓ | ✓✓ | ✓ | - |

## Getting Started

1. **Pick a model** based on the use case above
2. **Navigate:** `cd ~/github/claude/sonnet/5.5` (or your choice)
3. **Create a project:** `mkdir my-first-project && cd my-first-project`
4. **Initialize:** `claude init` (turns it into a git repo)
5. **Start working:** `claude` launches Claude Code in that project

## Cost Optimization Tips

- **Default to Opus 5.5** — unless you need Fable's extreme capability
- **Use Sonnet 5.5** for agents and iterative work
- **Use Haiku 5.5** for high-volume, simple tasks
- **Effort tuning** — lower `effort` within a model beats switching to cheaper models
- **Caching** — saves 90% on repeat requests to the same system prompt
