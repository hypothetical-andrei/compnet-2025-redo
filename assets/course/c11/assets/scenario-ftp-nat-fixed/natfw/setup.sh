#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
  iptables \
  iproute2 \
  iputils-ping \
  tcpdump

# Enable IPv4 forwarding without requiring the sysctl binary.
echo 1 > /proc/sys/net/ipv4/ip_forward

CLIENT_IF="eth0"
SERVER_IF="eth1"

iptables -F
iptables -t nat -F

iptables -t nat -A POSTROUTING -o "$SERVER_IF" -j MASQUERADE
iptables -A FORWARD -i "$CLIENT_IF" -o "$SERVER_IF" -j ACCEPT
iptables -A FORWARD -i "$SERVER_IF" -o "$CLIENT_IF" -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

echo "NAT/FW ready"
echo "Routes:"
ip route
echo "iptables:"
iptables -L -v -n
echo "nat table:"
iptables -t nat -L -v -n

tail -f /dev/null
