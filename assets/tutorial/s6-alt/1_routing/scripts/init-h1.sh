#!/bin/sh
# init-h1.sh — configurare rute pentru h1
# IP-ul (10.0.1.2/29) este setat static de compose via ipv4_address.
# Aici doar adăugăm ruta implicită spre r1.

sleep 2

ip route add default via 10.0.1.1 2>/dev/null || true

echo "[h1] Configurare completă"
ip a
ip route

exec sleep infinity
