# 1. Choosing a Distro

There's no single "best" distro — the right choice depends on what you're optimizing for.
Use this decision guide, then read the matching package-management section.

## Decision Guide

**"I want it to just work, with the biggest community for Googling problems."**
→ **Ubuntu LTS** (22.04/24.04). Huge ecosystem, every tutorial targets it, 5 years of
security updates per LTS release. Default choice for servers and VPS hosting.

**"I want stability above all else — a server I set up once and barely touch."**
→ **Debian Stable**. Slower-moving than Ubuntu, extremely well-tested packages,
no corporate strings attached. The base Ubuntu is built on.

**"I want the newest packages and I'm willing to read release notes."**
→ **Fedora**. Rolling ~6-month releases, close to upstream GNOME/kernel, RHEL's
upstream testing ground. Good middle ground between bleeding-edge and stable.

**"I want enterprise support contracts (RHEL, SLES) or their free clones."**
→ **Rocky Linux / AlmaLinux** (RHEL clones, free) for servers, or **RHEL** itself if
you're paying for support. **openSUSE Leap** if you want SUSE's tooling (YaST, Btrfs
snapshots by default) without the SLES subscription.

**"I want full control, a minimal base, and I don't mind reading the wiki."**
→ **Arch Linux**. Rolling release, you build up the system yourself, the **Arch Wiki**
is the best Linux documentation on the internet regardless of what distro you run.
Steeper learning curve, but you understand every piece of your system.

**"I want Arch's packages but a working system out of the box."**
→ **Manjaro** or **EndeavourOS**. Both use pacman and the Arch repos but give you a
sane default install. EndeavourOS is closer to vanilla Arch; Manjaro delays updates
slightly for extra testing.

**"I'm setting up containers, a minimal VM, or an embedded device."**
→ **Alpine Linux**. Tiny (musl libc + busybox), fast boot, the default base for most
Docker images. Not meant as a daily-driver desktop.

**"I want an immutable, hard-to-break desktop or server."**
→ **Fedora Silverblue/Kinoite** (desktop) or **Fedora CoreOS** (servers/containers).
Atomic updates, rollback built in.

## Quick Comparison

| Distro | Package Mgr | Release Model | Best For |
|---|---|---|---|
| Ubuntu | apt (.deb) | 6mo / 2yr LTS | Servers, beginners, cloud |
| Debian | apt (.deb) | ~2yr stable | Long-lived servers |
| Fedora | dnf (.rpm) | ~6mo | Desktops, latest GNOME/kernel |
| RHEL/Rocky/Alma | dnf (.rpm) | ~5-10yr | Enterprise, compliance |
| openSUSE | zypper (.rpm) | Leap ~1yr / Tumbleweed rolling | Desktop + server, snapshots |
| Arch | pacman | Rolling | Full control, learning |
| Manjaro/EndeavourOS | pacman | Rolling | Arch without the install pain |
| Alpine | apk | Rolling | Containers, minimal systems |

## What This Guide Assumes

The rest of this guide covers **pacman** (Arch family), **apt** (Debian/Ubuntu family),
and **dnf** (Fedora/RHEL family) — between them these cover the vast majority of real
systems. Everything after the package-management sections (systemd, networking,
storage, security) is distro-agnostic; the commands are the same regardless of which
package manager put the binaries there.
