import ipaddress
import os
import socket
import struct

TCP_LISTEN = "0A"


def decode_addr(hexaddr):
    """'0100007F:0050' (IPv4) or 32-hex-digit IPv6 form -> (ip, port)."""
    host, port = hexaddr.split(":")
    raw = bytes.fromhex(host)
    if len(raw) == 4:
        ip = socket.inet_ntoa(raw[::-1])
    else:  # /proc stores IPv6 as four little-endian 32-bit words
        words = struct.unpack("<4I", raw)
        ip = str(ipaddress.IPv6Address(struct.pack(">4I", *words)))
    return ip, int(port, 16)


def parse_proc_net(text):
    """Return listening sockets as dicts: ip, port, inode."""
    out = []
    for line in text.splitlines()[1:]:
        f = line.split()
        if len(f) < 10 or f[3] != TCP_LISTEN:
            continue
        ip, port = decode_addr(f[1])
        out.append({"ip": ip, "port": port, "inode": f[9]})
    return out


def inode_owners():
    """Map socket inode -> (pid, name). Only sees processes we may inspect."""
    owners = {}
    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            fds = os.listdir(f"/proc/{pid}/fd")
            with open(f"/proc/{pid}/comm") as f:
                name = f.read().strip()
        except OSError:
            continue
        for fd in fds:
            try:
                target = os.readlink(f"/proc/{pid}/fd/{fd}")
            except OSError:
                continue
            if target.startswith("socket:["):
                owners[target[8:-1]] = (int(pid), name)
    return owners


def scope(ip):
    addr = ipaddress.ip_address(ip)
    if addr.is_loopback:
        return "localhost only"
    if addr.is_unspecified:
        return "all interfaces"
    return "single interface"


def listening():
    sockets = []
    for path in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(path) as f:
                sockets += parse_proc_net(f.read())
        except OSError:
            pass
    owners = inode_owners()
    for s in sockets:
        s["pid"], s["process"] = owners.get(s["inode"], (None, "-"))
        s["scope"] = scope(s["ip"])
        s["exposed"] = s["scope"] != "localhost only"
    return sorted(sockets, key=lambda s: s["port"])
