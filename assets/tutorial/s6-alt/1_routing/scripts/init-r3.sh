#!/bin/sh
# init-r3.sh — configurare IP și rute pentru r3
#
# r3 este conectat la 3 rețele:
#   net_r2_r3  : 10.0.23.0/29  → r3 primește 10.0.23.2/29
#   net_r1_r3  : 10.0.13.0/29  → r3 primește 10.0.13.2/29
#   net_r3_h3  : 10.0.3.0/29   → r3 primește 10.0.3.1/29

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
# Interfața spre r2 (net_r2_r3, 10.0.23.0/29)
# ---------------------------------------------------------------------------
echo "[r3] Caut interfața spre r2 (10.0.23.x)..."
IFACE_R2=$(find_iface_by_prefix "10.0.23.")
if [ -z "$IFACE_R2" ]; then
    echo "[r3] EROARE: nu am găsit interfața pentru net_r2_r3" >&2
    exit 1
fi
echo "[r3] Interfața spre r2: $IFACE_R2"
ip addr flush dev "$IFACE_R2" 2>/dev/null || true
ip addr add 10.0.23.2/29 dev "$IFACE_R2"
ip link set "$IFACE_R2" up

# ---------------------------------------------------------------------------
# Interfața spre r1 (net_r1_r3, 10.0.13.0/29)
# ---------------------------------------------------------------------------
echo "[r3] Caut interfața spre r1 (10.0.13.x)..."
IFACE_R1=$(find_iface_by_prefix "10.0.13.")
if [ -z "$IFACE_R1" ]; then
    echo "[r3] EROARE: nu am găsit interfața pentru net_r1_r3" >&2
    exit 1
fi
echo "[r3] Interfața spre r1: $IFACE_R1"
ip addr flush dev "$IFACE_R1" 2>/dev/null || true
ip addr add 10.0.13.2/29 dev "$IFACE_R1"
ip link set "$IFACE_R1" up

# ---------------------------------------------------------------------------
# Interfața spre h3 (net_r3_h3, 10.0.3.0/29)
# ---------------------------------------------------------------------------
echo "[r3] Caut interfața spre h3 (10.0.3.x)..."
IFACE_H3=$(find_iface_by_prefix "10.0.3.")
if [ -z "$IFACE_H3" ]; then
    echo "[r3] EROARE: nu am găsit interfața pentru net_r3_h3" >&2
    exit 1
fi
echo "[r3] Interfața spre h3: $IFACE_H3"
ip addr flush dev "$IFACE_H3" 2>/dev/null || true
ip addr add 10.0.3.1/29 dev "$IFACE_H3"
ip link set "$IFACE_H3" up

# ---------------------------------------------------------------------------
# Rute inițiale — calea activă: h1 -> r1 -> r3 -> h3
# ---------------------------------------------------------------------------
ip route add 10.0.1.0/29 via 10.0.13.1 2>/dev/null || true

echo "[r3] Configurare completă"
ip a
ip route

exec sleep infinity
