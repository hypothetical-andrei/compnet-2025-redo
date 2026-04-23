#!/bin/sh
# init-h3.sh — configurare rute pentru h3
# IP-ul (10.0.3.2/29) este setat static de compose via ipv4_address.
# Aici doar adăugăm ruta implicită spre r3.

sleep 2

ip route add default via 10.0.3.1 2>/dev/null || true

echo "[h3] Configurare completă"
ip a
ip route

exec sleep infinity
