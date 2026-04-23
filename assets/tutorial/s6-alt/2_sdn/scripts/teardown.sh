#!/usr/bin/env bash
# =============================================================================
# teardown.sh — curata complet lab-ul SDN
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# 1. Containere (toate versiunile cunoscute ale lab-ului)
# ---------------------------------------------------------------------------
echo "[teardown] Sterg containerele asociate lab-ului..."
ALL_CONTAINERS=$(podman ps -a --format '{{.Names}}' 2>/dev/null || true)
for CNAME in sdn-controller sdn-topology sdn-ovs sdn-h1 sdn-h2 sdn-h3; do
  if echo "$ALL_CONTAINERS" | grep -qx "$CNAME"; then
    podman rm -f "$CNAME" && echo "  sters: $CNAME"
  else
    echo "  nu exista: $CNAME (ok)"
  fi
done

# ---------------------------------------------------------------------------
# 2. Retele Podman — orice retea cu 'sdn' in nume
# ---------------------------------------------------------------------------
echo ""
echo "[teardown] Sterg retelele Podman asociate lab-ului..."
FOUND_NET=0
while IFS= read -r NET; do
  if [[ "$NET" =~ sdn ]]; then
    FOUND_NET=1
    podman network rm "$NET" 2>/dev/null \
      && echo "  stearsa: $NET" \
      || echo "  nu am putut sterge: $NET"
  fi
done < <(podman network ls --format '{{.Name}}' | grep -v '^podman$')
[[ $FOUND_NET -eq 0 ]] && echo "  nicio retea sdn gasita (ok)"

# ---------------------------------------------------------------------------
# 3. Bridge-uri kernel ramase din sesiuni anterioare cu subnet 172.30.x
#    (sesiunile noi nu au subnet fix deci nu lasa bridge-uri cu IP cunoscut)
# ---------------------------------------------------------------------------
echo ""
echo "[teardown] Sterg bridge-uri kernel ramase cu 172.30.x (sesiuni vechi)..."
FOUND_BR=0
while IFS= read -r LINE; do
  BR=$(echo "$LINE" | awk '{print $3}')
  if [[ -n "$BR" ]] && ip link show "$BR" &>/dev/null; then
    FOUND_BR=1
    sudo ip link set "$BR" down 2>/dev/null || true
    sudo ip link del "$BR" 2>/dev/null \
      && echo "  sters: $BR" \
      || echo "  nu am putut sterge: $BR"
  fi
done < <(ip route show | grep "172\.30\.")
[[ $FOUND_BR -eq 0 ]] && echo "  niciun bridge ramas (ok)"

# ---------------------------------------------------------------------------
# 4. podman-compose down
# ---------------------------------------------------------------------------
echo ""
echo "[teardown] podman-compose down..."
podman-compose down --volumes 2>/dev/null \
  || podman compose down --volumes 2>/dev/null \
  || echo "  (nimic de oprit)"

echo ""
echo "[teardown] Gata. Mediul este curat."
