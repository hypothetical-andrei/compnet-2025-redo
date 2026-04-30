#!/usr/bin/env bash
# =============================================================================
# teardown.sh — curata complet lab-ul Seminar 7
# =============================================================================
set -euo pipefail

echo "[teardown] Opresc si sterg containerele..."
for CNAME in h1 h2; do
  if podman container exists "$CNAME" 2>/dev/null; then
    podman rm -f "$CNAME" && echo "  sters: $CNAME"
  else
    echo "  nu exista: $CNAME (ok)"
  fi
done

echo ""
echo "[teardown] Sterg retelele Podman asociate lab-ului..."
while IFS= read -r NET; do
  if [[ "$NET" =~ sem7 ]]; then
    podman network rm "$NET" 2>/dev/null \
      && echo "  stearsa: $NET" \
      || echo "  nu am putut sterge: $NET"
  fi
done < <(podman network ls --format '{{.Name}}' | grep -v '^podman$')

echo ""
echo "[teardown] podman-compose down..."
podman-compose down --volumes 2>/dev/null \
  || podman compose down --volumes 2>/dev/null \
  || echo "  (nimic de oprit)"

echo ""
echo "[teardown] Gata."
