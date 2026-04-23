#!/bin/sh
# cleanup.sh — curăță containerele și rețelele rămase de la o rulare anterioară
#
# Rulați acest script dacă primiți eroarea:
#   "Error: subnet X.X.X.X/XX is already used on the host or by another config"
#
# Utilizare:
#   sh cleanup.sh

PROJECT="1_routing"

echo "[cleanup] Opresc și șterg containerele..."
for CONTAINER in h1 h3 r1 r2 r3; do
    podman rm -f "$CONTAINER" 2>/dev/null && echo "  removed container $CONTAINER" || echo "  $CONTAINER not found, skipping"
done

echo "[cleanup] Șterg rețelele..."
for NET in net_h1_r1 net_r1_r2 net_r2_r3 net_r1_r3 net_r3_h3; do
    FULL_NAME="${PROJECT}_${NET}"
    podman network rm "$FULL_NAME" 2>/dev/null && echo "  removed network $FULL_NAME" || echo "  $FULL_NAME not found, skipping"
done

echo "[cleanup] Gata. Puteți rula acum: podman-compose -f 1b_podman-compose.yaml up -d"
