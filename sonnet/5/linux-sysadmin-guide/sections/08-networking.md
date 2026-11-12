# 8. Networking

## Checking Interfaces and Addresses

```bash
ip addr show          # (ip a) — modern replacement for ifconfig
ip link show          # (ip l) — interface status, up/down
ip route show          # (ip r) — routing table / default gateway
```

## Connectivity Testing

```bash
ping -c 4 8.8.8.8                 # basic reachability
traceroute example.com             # path to a host (mtr is a better interactive version)
mtr example.com                    # live, continuously-updating traceroute
dig example.com                    # DNS lookup, full detail
dig +short example.com             # DNS lookup, just the answer
nslookup example.com               # simpler DNS lookup
host example.com                   # another simple DNS lookup
curl -I https://example.com        # fetch headers only — quick HTTP check
```

## What's Listening / Connected

```bash
ss -tulpn          # modern replacement for netstat: TCP/UDP listeners + owning process
ss -tn state established    # active established TCP connections

# per-process:
sudo lsof -i :443                  # what's using port 443
sudo lsof -i -P -n | grep LISTEN   # everything listening, no DNS/port-name resolution
```

## Firewalls

### ufw (Debian/Ubuntu/Arch — simplest)

```bash
sudo ufw status verbose
sudo ufw allow 22/tcp
sudo ufw allow from 192.168.1.0/24 to any port 5432
sudo ufw delete allow 22/tcp
sudo ufw enable
```

### firewalld (Fedora/RHEL — zone-based)

```bash
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=public --add-service=http --permanent
sudo firewall-cmd --zone=public --add-port=8080/tcp --permanent
sudo firewall-cmd --reload              # required after any --permanent change
sudo firewall-cmd --list-all
```

### nftables / iptables (lower level, underneath both of the above)

```bash
sudo nft list ruleset      # current nftables rules
sudo iptables -L -n -v      # legacy iptables view (still used directly on some systems)
```

## Static IP / DNS Configuration

### Debian/Ubuntu — netplan (`/etc/netplan/*.yaml`)

```yaml
network:
  version: 2
  ethernets:
    eth0:
      addresses: [192.168.1.50/24]
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [1.1.1.1, 8.8.8.8]
```

```bash
sudo netplan apply
```

### NetworkManager (Fedora, Arch desktops, many others)

```bash
nmcli device status
nmcli connection show
sudo nmcli connection modify "Wired connection 1" ipv4.addresses 192.168.1.50/24
sudo nmcli connection modify "Wired connection 1" ipv4.gateway 192.168.1.1
sudo nmcli connection modify "Wired connection 1" ipv4.dns "1.1.1.1 8.8.8.8"
sudo nmcli connection modify "Wired connection 1" ipv4.method manual
sudo nmcli connection up "Wired connection 1"
```

### systemd-networkd (minimal servers, containers)

`/etc/systemd/network/20-wired.network`:

```ini
[Match]
Name=eth0

[Network]
Address=192.168.1.50/24
Gateway=192.168.1.1
DNS=1.1.1.1
```

```bash
sudo systemctl restart systemd-networkd
```

## SSH

```bash
ssh-keygen -t ed25519 -C "you@host"      # generate a modern keypair
ssh-copy-id user@remote-host              # push your public key to a server
ssh -i ~/.ssh/id_ed25519 user@host        # connect with a specific key
scp file.txt user@host:/remote/path/      # copy a file over SSH
rsync -avz ./localdir/ user@host:/remote/dir/   # efficient sync, resumable
```

`~/.ssh/config` for shortcuts:

```
Host myserver
    HostName 203.0.113.10
    User alice
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
```

Then just: `ssh myserver`
