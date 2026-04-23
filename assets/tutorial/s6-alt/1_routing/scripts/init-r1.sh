#!/bin/sh
# init-r1.sh — configurare IP și rute pentru r1
#
# r1 este conectat la 3 rețele:
#   net_h1_r1  : 10.0.1.0/29   → r1 primește 10.0.1.1/29
#   net_r1_r2  : 10.0.12.0/29  → r1 primește 10.0.12.1/29
#   net_r1_r3  : 10.0.13.0/29  → r1 primește 10.0.13.1/29

# Pauză inițială — așteptăm ca r2 și r3 să pornească și să se alăture rețelelor
sleep 5

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
# Interfața spre h1 (net_h1_r1, 10.0.1.0/29)
# ---------------------------------------------------------------------------
echo "[r1] Caut interfața spre h1 (10.0.1.x)..."
IFACE_H1=$(find_iface_by_prefix "10.0.1.")
if [ -z "$IFACE_H1" ]; then
    echo "[r1] EROARE: nu am găsit interfața pentru net_h1_r1" >&2
    exit 1
fi
echo "[r1] Interfața spre h1: $IFACE_H1"
ip addr flush dev "$IFACE_H1" 2>/dev/null || true
ip addr add 10.0.1.1/29 dev "$IFACE_H1"
ip link set "$IFACE_H1" up

# ---------------------------------------------------------------------------
# Interfața spre r2 (net_r1_r2, 10.0.12.0/29)
# ---------------------------------------------------------------------------
echo "[r1] Caut interfața spre r2 (10.0.12.x)..."
IFACE_R2=$(find_iface_by_prefix "10.0.12.")
if [ -z "$IFACE_R2" ]; then
    echo "[r1] EROARE: nu am găsit interfața pentru net_r1_r2" >&2
    exit 1
fi
echo "[r1] Interfața spre r2: $IFACE_R2"
ip addr flush dev "$IFACE_R2" 2>/dev/null || true
ip addr add 10.0.12.1/29 dev "$IFACE_R2"
ip link set "$IFACE_R2" up

# ---------------------------------------------------------------------------
# Interfața spre r3 (net_r1_r3, 10.0.13.0/29)
# ---------------------------------------------------------------------------
echo "[r1] Caut interfața spre r3 (10.0.13.x)..."
IFACE_R3=$(find_iface_by_prefix "10.0.13.")
if [ -z "$IFACE_R3" ]; then
    echo "[r1] EROARE: nu am găsit interfața pentru net_r1_r3" >&2
    exit 1
fi
echo "[r1] Interfața spre r3: $IFACE_R3"
ip addr flush dev "$IFACE_R3" 2>/dev/null || true
ip addr add 10.0.13.1/29 dev "$IFACE_R3"
ip link set "$IFACE_R3" up

# ---------------------------------------------------------------------------
# Rute inițiale — calea activă: h1 -> r1 -> r3 -> h3
# r2 este izolat: r1 nu trimite trafic prin r2 la pornire
# ---------------------------------------------------------------------------
ip route add 10.0.3.0/29 via 10.0.13.2 2>/dev/null || true

echo "[r1] Configurare completă"
ip a
ip route

exec sleep infinity
