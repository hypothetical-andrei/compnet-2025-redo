#!/bin/sh
# init-r2.sh — configurare IP pentru r2
#
# r2 este conectat la 2 rețele:
#   net_r1_r2  : 10.0.12.0/30  → r2 primește 10.0.12.2/30
#   net_r2_r3  : 10.0.23.0/30  → r2 primește 10.0.23.1/30
#
# La pornire, r2 nu are rute spre h1 sau h3 — este izolat intenționat.
# Studentul va adăuga rutele manual în exercițiu.

set -e
sleep 2

find_iface_by_prefix() {
    PREFIX="$1"
    ip -o addr show | awk -v p="$PREFIX" '$4 ~ p {print $2}' | grep -v lo | head -n1
}

# ---------------------------------------------------------------------------
# Interfața spre r1 (net_r1_r2, 10.0.12.0/30)
# ---------------------------------------------------------------------------
IFACE_R1=$(find_iface_by_prefix "10.0.12.")
if [ -z "$IFACE_R1" ]; then
    echo "[r2] EROARE: nu am găsit interfața pentru net_r1_r2 (10.0.12.x)" >&2
    exit 1
fi
echo "[r2] Interfața spre r1: $IFACE_R1"
ip addr flush dev "$IFACE_R1"
ip addr add 10.0.12.2/30 dev "$IFACE_R1"
ip link set "$IFACE_R1" up

# ---------------------------------------------------------------------------
# Interfața spre r3 (net_r2_r3, 10.0.23.0/30)
# ---------------------------------------------------------------------------
IFACE_R3=$(find_iface_by_prefix "10.0.23.")
if [ -z "$IFACE_R3" ]; then
    echo "[r2] EROARE: nu am găsit interfața pentru net_r2_r3 (10.0.23.x)" >&2
    exit 1
fi
echo "[r2] Interfața spre r3: $IFACE_R3"
ip addr flush dev "$IFACE_R3"
ip addr add 10.0.23.1/30 dev "$IFACE_R3"
ip link set "$IFACE_R3" up

# ---------------------------------------------------------------------------
# IP Forwarding activat, dar fără rute spre hosturi — r2 este izolat
# ---------------------------------------------------------------------------
sysctl -w net.ipv4.ip_forward=1

echo "[r2] Configurare completă — r2 este izolat (fără rute spre h1/h3)"
ip a
ip route

exec sleep infinity
