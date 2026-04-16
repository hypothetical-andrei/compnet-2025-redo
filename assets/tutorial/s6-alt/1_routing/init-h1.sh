#!/bin/sh
# init-h1.sh — configurare IP și rute pentru h1
# Legătură: h1 <-> r1 via net_h1_r1 (10.0.1.0/30)
# h1 primește o singură interfață externă (prima care nu este lo)

set -e

# Așteptăm ca interfețele să fie disponibile
sleep 1

# Identificăm interfața conectată la net_h1_r1 (singura interfață non-lo)
IFACE=$(ip -o link show | awk -F': ' '$2 != "lo" {print $2}' | head -n1)

echo "[h1] Configurez interfața $IFACE cu 10.0.1.2/30"
ip addr flush dev "$IFACE"
ip addr add 10.0.1.2/30 dev "$IFACE"
ip link set "$IFACE" up

# Rută implicită spre r1
ip route add default via 10.0.1.1

echo "[h1] Configurare completă"
ip a
ip route

# Menținem containerul activ
exec sleep infinity
