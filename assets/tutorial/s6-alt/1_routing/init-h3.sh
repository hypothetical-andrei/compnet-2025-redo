#!/bin/sh
# init-h3.sh — configurare IP și rute pentru h3
# Legătură: h3 <-> r3 via net_r3_h3 (10.0.3.0/30)

set -e

sleep 1

IFACE=$(ip -o link show | awk -F': ' '$2 != "lo" {print $2}' | head -n1)

echo "[h3] Configurez interfața $IFACE cu 10.0.3.2/30"
ip addr flush dev "$IFACE"
ip addr add 10.0.3.2/30 dev "$IFACE"
ip link set "$IFACE" up

# Rută implicită spre r3
ip route add default via 10.0.3.1

echo "[h3] Configurare completă"
ip a
ip route

exec sleep infinity
