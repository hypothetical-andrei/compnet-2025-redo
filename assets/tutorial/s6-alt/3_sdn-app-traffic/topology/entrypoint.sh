#!/usr/bin/env bash
# =============================================================================
# entrypoint.sh — topologie SDN completa intr-un singur container
# =============================================================================
set -e

CONTROLLER_IP="${CONTROLLER_IP:-controller}"
BRIDGE="s1"

# ---------------------------------------------------------------------------
# 1. Pornire OVS
# ---------------------------------------------------------------------------
echo "[topo] Initializez baza de date OVS..."
mkdir -p /var/run/openvswitch /var/log/openvswitch /etc/openvswitch

if [ ! -f /etc/openvswitch/conf.db ]; then
    ovsdb-tool create /etc/openvswitch/conf.db \
        /usr/share/openvswitch/vswitch.ovsschema
    echo "[topo] conf.db creat."
fi

echo "[topo] Pornesc ovsdb-server..."
ovsdb-server /etc/openvswitch/conf.db \
    --remote=punix:/var/run/openvswitch/db.sock \
    --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
    --pidfile=/var/run/openvswitch/ovsdb-server.pid \
    --detach \
    --log-file=/var/log/openvswitch/ovsdb-server.log

ovs-vsctl --no-wait init

echo "[topo] Pornesc ovs-vswitchd..."
ovs-vswitchd \
    --pidfile=/var/run/openvswitch/ovs-vswitchd.pid \
    --detach \
    --log-file=/var/log/openvswitch/ovs-vswitchd.log

echo "[topo] OVS pornit."

# ---------------------------------------------------------------------------
# 2. Creare bridge s1
# ---------------------------------------------------------------------------
if ovs-vsctl br-exists "$BRIDGE" 2>/dev/null; then
    echo "[topo] Sterg bridge $BRIDGE din rulare anterioara..."
    ovs-vsctl del-br "$BRIDGE"
fi

ovs-vsctl add-br "$BRIDGE"
ovs-vsctl set bridge "$BRIDGE" protocols=OpenFlow13
ovs-vsctl set-fail-mode "$BRIDGE" secure

echo "[topo] Bridge $BRIDGE creat."

# ---------------------------------------------------------------------------
# 3. Creare hosturi ca namespace-uri cu procese sentinel
# ---------------------------------------------------------------------------
setup_host() {
    local NS="$1"
    local IP="$2"
    local MAC="$3"
    local PORT="$4"
    local VETH="veth-${NS}"
    local PEER="veth-${NS}-peer"
    local PIDFILE="/var/run/host-${NS}.pid"

    echo "[topo] Configurez ${NS} (${IP}, MAC ${MAC}, port OVS ${PORT})..."

    ip netns del "$NS" 2>/dev/null || true
    ip link del "$VETH" 2>/dev/null || true

    ip netns add "$NS"

    nsenter --net="/var/run/netns/${NS}" -- sleep infinity &
    echo $! > "$PIDFILE"
    local PID=$!

    ip link add "$VETH" type veth peer name "$PEER"
    ip link set "$PEER" netns "$PID"

    nsenter --net="/proc/${PID}/ns/net" -- ip link set "$PEER" name eth0
    nsenter --net="/proc/${PID}/ns/net" -- ip link set eth0 address "$MAC"
    nsenter --net="/proc/${PID}/ns/net" -- ip addr add "$IP" dev eth0
    nsenter --net="/proc/${PID}/ns/net" -- ip link set eth0 up
    nsenter --net="/proc/${PID}/ns/net" -- ip link set lo up

    ip link set "$VETH" up

    ovs-vsctl add-port "$BRIDGE" "$VETH" \
        -- set Interface "$VETH" ofport_request="$PORT"

    echo "[topo]   OK: ${NS} (PID=${PID}) eth0=${IP} -> ${BRIDGE}:port${PORT}"
}

setup_host h1 "10.0.10.1/24" "00:00:00:00:00:01" 1
setup_host h2 "10.0.10.2/24" "00:00:00:00:00:02" 2
setup_host h3 "10.0.10.3/24" "00:00:00:00:00:03" 3

# ---------------------------------------------------------------------------
# 4. Helpere accesibile din podman exec
# ---------------------------------------------------------------------------

# 'host hX cmd' — ruleaza o comanda in namespace-ul unui host
cat > /usr/local/bin/host << 'EOF'
#!/usr/bin/env bash
NS="$1"; shift
PIDFILE="/var/run/host-${NS}.pid"
if [ ! -f "$PIDFILE" ]; then echo "Host $NS nu exista." >&2; exit 1; fi
PID=$(cat "$PIDFILE")
nsenter --net="/proc/${PID}/ns/net" -- "$@"
EOF
chmod +x /usr/local/bin/host

# 'bg hX <nume> cmd...' — porneste un server in background intr-un namespace
# Log disponibil la: /var/log/bg-hX-<nume>.log
cat > /usr/local/bin/bg << 'EOF'
#!/usr/bin/env bash
NS="$1"; NAME="$2"; shift 2
PIDFILE="/var/run/host-${NS}.pid"
BGPIDFILE="/var/run/bg-${NS}-${NAME}.pid"
if [ ! -f "$PIDFILE" ]; then echo "Host $NS nu exista." >&2; exit 1; fi
PID=$(cat "$PIDFILE")
nohup nsenter --net="/proc/${PID}/ns/net" -- "$@" \
    > "/var/log/bg-${NS}-${NAME}.log" 2>&1 &
echo $! > "$BGPIDFILE"
echo "[bg] $NS/$NAME pornit (PID=$!, log=/var/log/bg-${NS}-${NAME}.log)"
EOF
chmod +x /usr/local/bin/bg

# 'bg-stop hX <nume>' — opreste un server pornit cu bg
cat > /usr/local/bin/bg-stop << 'EOF'
#!/usr/bin/env bash
NS="$1"; NAME="$2"
BGPIDFILE="/var/run/bg-${NS}-${NAME}.pid"
if [ ! -f "$BGPIDFILE" ]; then echo "Niciun proces bg $NS/$NAME gasit." >&2; exit 1; fi
kill "$(cat "$BGPIDFILE")" 2>/dev/null \
    && echo "[bg-stop] $NS/$NAME oprit" \
    || echo "[bg-stop] procesul nu mai ruleaza"
rm -f "$BGPIDFILE"
EOF
chmod +x /usr/local/bin/bg-stop

# ---------------------------------------------------------------------------
# 5. Conectare la controller
# ---------------------------------------------------------------------------
echo ""
echo "[topo] Conectez $BRIDGE la controller: tcp:${CONTROLLER_IP}:6633"
ovs-vsctl set-controller "$BRIDGE" "tcp:${CONTROLLER_IP}:6633"

echo ""
echo "========================================================"
echo " Topologie SDN gata:"
echo "   h1 (10.0.10.1) -- s1:port1"
echo "   h2 (10.0.10.2) -- s1:port2"
echo "   h3 (10.0.10.3) -- s1:port3"
echo "   controller: tcp:${CONTROLLER_IP}:6633"
echo ""
echo " Comenzi utile:"
echo "   podman exec sdn-topology host h1 ping -c3 10.0.10.2"
echo "   podman exec sdn-topology bg h2 tcp-server python3 /apps/tcp_server.py 5000"
echo "   podman exec -it sdn-topology host h1 python3 /apps/tcp_client.py 10.0.10.2 5000"
echo "   podman exec sdn-topology ovs-ofctl -O OpenFlow13 dump-flows s1"
echo "========================================================"

tail -f /var/log/openvswitch/ovs-vswitchd.log
