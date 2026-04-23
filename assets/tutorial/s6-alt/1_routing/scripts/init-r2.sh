#!/bin/sh
# init-r2.sh — configurare IP pentru r2
#
# r2 este conectat la 2 rețele:
#   net_r1_r2  : 10.0.12.0/29  → r2 primește 10.0.12.2/29
#   net_r2_r3  : 10.0.23.0/29  → r2 primește 10.0.23.1/29

sleep 3

# Funcție: găsește interfața care are o adresă în subnetul dat, cu retry
find_iface_by_prefix() {
    PREFIX="$1"
    RETRIES=30
    while [ $RETRIES -gt 0 ]; do
        IFACE=$(ip -o addr show | awk -v p="$PREFIX" '$4 ~ p {print $2}' | grep -v lo | head -n1)
        if [ -n "$IFACE" ]; then
            echo "$IFACE"
            return 0
        fi
        RETRIES=$((RETRIES - 1))
        sleep 2
    done
    return 1
}

# ---------------------------------------------------------------------------
# Interfața spre r1 (net_r1_r2, 10.0.12.0/29)
# ---------------------------------------------------------------------------
echo "[r2] Caut interfața spre r1 (10.0.12.x)..."
IFACE_R1=$(find_iface_by_prefix "10.0.12.")
if [ -z "$IFACE_R1" ]; then
    echo "[r2] EROARE: nu am găsit interfața pentru net_r1_r2" >&2
    exit 1
fi
echo "[r2] Interfața spre r1: $IFACE_R1"
ip addr flush dev "$IFACE_R1" 2>/dev/null || true
ip addr add 10.0.12.2/29 dev "$IFACE_R1"
ip link set "$IFACE_R1" up

# ---------------------------------------------------------------------------
# Interfața spre r3 (net_r2_r3, 10.0.23.0/29)
# ---------------------------------------------------------------------------
echo "[r2] Caut interfața spre r3 (10.0.23.x)..."
IFACE_R3=$(find_iface_by_prefix "10.0.23.")
if [ -z "$IFACE_R3" ]; then
    echo "[r2] EROARE: nu am găsit interfața pentru net_r2_r3" >&2
    exit 1
fi
echo "[r2] Interfața spre r3: $IFACE_R3"
ip addr flush dev "$IFACE_R3" 2>/dev/null || true
ip addr add 10.0.23.1/29 dev "$IFACE_R3"
ip link set "$IFACE_R3" up

echo "[r2] Configurare completă — r2 este izolat (fără rute spre h1/h3)"
ip a
ip route

exec sleep infinity
