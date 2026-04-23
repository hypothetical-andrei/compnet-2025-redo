#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

LOSS="${1:-20}"

echo "[run] starting Mininet scenario with loss=${LOSS}% (requires sudo)"

sudo python3 - <<PY
import time
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.log import setLogLevel

setLogLevel("warning")

loss = float("${LOSS}")

net = Mininet(controller=OVSController, link=TCLink, autoSetMacs=True)
net.addController("c0")
h1 = net.addHost("h1", ip="10.0.0.1/24")
h2 = net.addHost("h2", ip="10.0.0.2/24")
s1 = net.addSwitch("s1")

net.addLink(h1, s1, loss=loss)
net.addLink(s1, h2, loss=loss)

net.start()

def wait_for_output(host, outfile, sentinel, timeout=60):
    """Poll outfile on host until sentinel string appears or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        out = host.cmd(f"cat {outfile} 2>/dev/null")
        if sentinel in out:
            return out.strip()
        time.sleep(0.3)
    return host.cmd(f"cat {outfile} 2>/dev/null").strip() + "\n[WARN] timed out waiting for receiver"

# ── UDP test ─────────────────────────────────────────────────────────────────
print("[run] UDP test  (best-effort — losses expected)")
h2.cmd("python3 udp_receiver.py > udp_receiver.out 2>&1 &")
time.sleep(0.2)
h1.cmd("python3 udp_sender.py > udp_sender.out 2>&1")
# UDP receiver has a built-in 5 s idle timeout; poll until it prints its summary.
out = wait_for_output(h2, "udp_receiver.out", "[udp_receiver]", timeout=15)
print(out)

# ── TCP test ──────────────────────────────────────────────────────────────────
print("\\n[run] TCP test  (reliable stream — no losses expected)")
h2.cmd("python3 tcp_receiver.py > tcp_receiver.out 2>&1 &")
time.sleep(0.2)
h1.cmd("python3 tcp_sender.py > tcp_sender.out 2>&1")
# The sender closes the connection when done; the receiver drains, then prints.
# On a 20%-loss link, TCP retransmissions can add 10-30 s — poll instead of sleeping.
out = wait_for_output(h2, "tcp_receiver.out", "[tcp_receiver]", timeout=60)
print(out)

net.stop()
PY

echo "[run] done"