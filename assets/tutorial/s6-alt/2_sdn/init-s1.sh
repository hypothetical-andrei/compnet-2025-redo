#!/bin/bash
# init-s1.sh — pornire Open vSwitch și conectare hosturi prin veth pairs
#
# Acest script rulează în containerul s1 (privilegiat).
# Pașii:
#   1. Pornește daemonii OVS (ovsdb-server, ovs-vswitchd)
#   2. Creează bridge-ul br0 și îl conectează la controller (TCP:controller:6633)
#   3. Creează câte o pereche veth pentru fiecare host
#   4. Mută câte un capăt al fiecărei perechi în namespace-ul de rețea al containerului host
#   5. Configurează IP și MAC pe capătul din container-ul host
#   6. Adaugă capătul din s1 la OVS (în ordine: h1=port1, h2=port2, h3=port3)

set -e

log() { echo "[s1] $*"; }

# ---------------------------------------------------------------------------
# 1. Pornire OVS
# ---------------------------------------------------------------------------
log "Inițializez baza de date OVS..."
mkdir -p /var/run/openvswitch /var/log/openvswitch /etc/openvswitch

# Inițializare bază de date dacă nu există
if [ ! -f /etc/openvswitch/conf.db ]; then
    ovsdb-tool create /etc/openvswitch/conf.db /usr/share/openvswitch/vswitch.ovsschema
fi

log "Pornesc ovsdb-server..."
ovsdb-server --remote=punix:/var/run/openvswitch/db.sock \
             --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
             --pidfile --detach --log-file=/var/log/openvswitch/ovsdb.log

log "Inițializez ovsdb..."
ovs-vsctl --no-wait init

log "Pornesc ovs-vswitchd..."
ovs-vswitchd --pidfile --detach --log-file=/var/log/openvswitch/vswitchd.log

sleep 1
log "OVS pornit. Versiune: $(ovs-vsctl --version | head -1)"

# ---------------------------------------------------------------------------
# 2. Creare bridge și conectare la controller
# ---------------------------------------------------------------------------
log "Creez bridge-ul br0..."
ovs-vsctl add-br br0
ovs-vsctl set bridge br0 protocols=OpenFlow13
ovs-vsctl set-controller br0 tcp:controller:6633
ovs-vsctl set bridge br0 fail_mode=secure

log "br0 creat. Aștept controllerul..."

# ---------------------------------------------------------------------------
# 3. Funcție helper: creare veth și mutare în namespace-ul unui container
# ---------------------------------------------------------------------------
# Parametri: <container_name> <veth_in_s1> <veth_in_host> <ip> <mac> <ofport>
connect_host() {
    CNAME="$1"    # numele containerului (ex: h1)
    VETH_S1="$2"  # capătul din s1 (ex: p-h1)
    VETH_H="$3"   # capătul din container-ul host (ex: h1-eth1)
    HOST_IP="$4"  # adresa IP a host-ului (ex: 10.0.10.1/24)
    HOST_MAC="$5" # MAC-ul dorit pe interfața host-ului
    OFPORT="$6"   # numărul de port OpenFlow dorit

    log "Conectez $CNAME (IP=$HOST_IP, MAC=$HOST_MAC, OF port=$OFPORT)..."

    # Găsim PID-ul containerului pentru a accesa network namespace-ul lui
    CPID=$(podman inspect --format '{{.State.Pid}}' "$CNAME" 2>/dev/null)
    if [ -z "$CPID" ] || [ "$CPID" = "0" ]; then
        log "EROARE: nu am putut găsi PID-ul pentru containerul $CNAME"
        return 1
    fi

    # Creăm symlink-ul namespace-ului (necesar pentru ip netns)
    mkdir -p /var/run/netns
    ln -sf "/proc/$CPID/ns/net" "/var/run/netns/$CNAME"

    # Creăm perechea veth
    ip link add "$VETH_S1" type veth peer name "$VETH_H"

    # Mutăm capătul host în namespace-ul containerului
    ip link set "$VETH_H" netns "$CNAME"

    # Configurăm capătul din s1
    ip link set "$VETH_S1" up

    # Configurăm capătul din container: IP, MAC, up
    ip netns exec "$CNAME" ip link set "$VETH_H" name eth1
    ip netns exec "$CNAME" ip link set eth1 address "$HOST_MAC"
    ip netns exec "$CNAME" ip addr add "$HOST_IP" dev eth1
    ip netns exec "$CNAME" ip link set eth1 up
    ip netns exec "$CNAME" ip route add default via 10.0.10.254 dev eth1 2>/dev/null || true

    # Adăugăm capătul s1 la OVS cu numărul de port OpenFlow specificat
    ovs-vsctl add-port br0 "$VETH_S1" -- set Interface "$VETH_S1" ofport_request="$OFPORT"

    log "$CNAME conectat pe OF port $OFPORT via $VETH_S1 <-> eth1"
}

# ---------------------------------------------------------------------------
# 4. Conectare hosturi
# Ordinea CONTEAZĂ: determină porturile OpenFlow (1, 2, 3)
# Trebuie să corespundă cu porturile hardcodate în controller:
#   h1=port1, h2=port2, h3=port3
# ---------------------------------------------------------------------------

# Așteptăm ca containerele host să fie pornite
log "Aștept containerele h1, h2, h3..."
for HOST in h1 h2 h3; do
    RETRIES=15
    while [ $RETRIES -gt 0 ]; do
        PID=$(podman inspect --format '{{.State.Pid}}' "$HOST" 2>/dev/null || echo "")
        if [ -n "$PID" ] && [ "$PID" != "0" ]; then
            log "$HOST este pornit (PID=$PID)"
            break
        fi
        sleep 1
        RETRIES=$((RETRIES - 1))
    done
    if [ $RETRIES -eq 0 ]; then
        log "EROARE: $HOST nu a pornit în timp util"
        exit 1
    fi
done

connect_host h1 p-h1 h1-eth1 10.0.10.1/24 00:00:00:00:00:01 1
connect_host h2 p-h2 h2-eth1 10.0.10.2/24 00:00:00:00:00:02 2
connect_host h3 p-h3 h3-eth1 10.0.10.3/24 00:00:00:00:00:03 3

# ---------------------------------------------------------------------------
# 5. Verificare finală
# ---------------------------------------------------------------------------
log "Configurare completă. Starea OVS:"
ovs-vsctl show
ovs-ofctl dump-flows br0 -O OpenFlow13 2>/dev/null || true

log "Porturile OpenFlow:"
ovs-ofctl dump-ports-desc br0 -O OpenFlow13 2>/dev/null || true

log "s1 este gata. Aștept controllerul să instaleze flow-uri..."

# Menținem containerul activ și afișăm logul OVS
exec tail -f /var/log/openvswitch/vswitchd.log
