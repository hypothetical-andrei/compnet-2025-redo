#!/bin/sh
# init-r1.sh — configurare IP și rute pentru r1
#
# r1 este conectat la 3 rețele:
#   net_h1_r1  : 10.0.1.0/30   → r1 primește 10.0.1.1/30
#   net_r1_r2  : 10.0.12.0/30  → r1 primește 10.0.12.1/30
#   net_r1_r3  : 10.0.13.0/30  → r1 primește 10.0.13.1/30
#
# Podman atribuie câte o adresă din fiecare subnet bridge pe interfețele
# containerului. Identificăm fiecare interfață după adresa DHCP primită
# de la bridge (care este în același subnet), apoi o înlocuim cu adresa statică.

set -e
sleep 2

# Funcție: găsește interfața care are deja o adresă în subnetul dat
# Parametru: prefixul de subnet (ex: "10.0.1.")
find_iface_by_prefix() {
    PREFIX="$1"
    ip -o addr show | awk -v p="$PREFIX" '$4 ~ p {print $2}' | grep -v lo | head -n1
}

# ---------------------------------------------------------------------------
# Interfața spre h1 (net_h1_r1, 10.0.1.0/30)
# ---------------------------------------------------------------------------
IFACE_H1=$(find_iface_by_prefix "10.0.1.")
if [ -z "$IFACE_H1" ]; then
    echo "[r1] EROARE: nu am găsit interfața pentru net_h1_r1 (10.0.1.x)" >&2
    exit 1
fi
echo "[r1] Interfața spre h1: $IFACE_H1"
ip addr flush dev "$IFACE_H1"
ip addr add 10.0.1.1/30 dev "$IFACE_H1"
ip link set "$IFACE_H1" up

# ---------------------------------------------------------------------------
# Interfața spre r2 (net_r1_r2, 10.0.12.0/30)
# ---------------------------------------------------------------------------
IFACE_R2=$(find_iface_by_prefix "10.0.12.")
if [ -z "$IFACE_R2" ]; then
    echo "[r1] EROARE: nu am găsit interfața pentru net_r1_r2 (10.0.12.x)" >&2
    exit 1
fi
echo "[r1] Interfața spre r2: $IFACE_R2"
ip addr flush dev "$IFACE_R2"
ip addr add 10.0.12.1/30 dev "$IFACE_R2"
ip link set "$IFACE_R2" up

# ---------------------------------------------------------------------------
# Interfața spre r3 (net_r1_r3, 10.0.13.0/30)
# ---------------------------------------------------------------------------
IFACE_R3=$(find_iface_by_prefix "10.0.13.")
if [ -z "$IFACE_R3" ]; then
    echo "[r1] EROARE: nu am găsit interfața pentru net_r1_r3 (10.0.13.x)" >&2
    exit 1
fi
echo "[r1] Interfața spre r3: $IFACE_R3"
ip addr flush dev "$IFACE_R3"
ip addr add 10.0.13.1/30 dev "$IFACE_R3"
ip link set "$IFACE_R3" up

# ---------------------------------------------------------------------------
# IP Forwarding
# ---------------------------------------------------------------------------
sysctl -w net.ipv4.ip_forward=1

# ---------------------------------------------------------------------------
# Rute inițiale — calea activă: h1 -> r1 -> r3 -> h3
# r2 este izolat: r1 nu trimite trafic prin r2 la pornire
# ---------------------------------------------------------------------------
ip route add 10.0.3.0/30 via 10.0.13.2

echo "[r1] Configurare completă"
ip a
ip route

exec sleep infinity
