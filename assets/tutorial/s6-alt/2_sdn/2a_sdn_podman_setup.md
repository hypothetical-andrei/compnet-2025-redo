# Setup: Topologia SDN cu Os-Ken și Podman (rootless)

În această versiune, tot lab-ul rulează fără `sudo`. Două containere sunt
suficiente: unul pentru controllerul Os-Ken și unul care conține OVS și
toate cele trei hosturi ca namespace-uri de rețea interne.

---

## Concept: un container pentru toată topologia

În loc să creăm veth-uri la nivelul host-ului (care necesita `sudo`), containerul
`topology` creează intern propriile namespace-uri de rețea:

```
┌─────────────────────────────────────────┐
│  container: sdn-topology                │
│                                         │
│  netns h1 (10.0.10.1) ──┐              │
│  netns h2 (10.0.10.2) ──┤── bridge s1  │
│  netns h3 (10.0.10.3) ──┘      │       │
└─────────────────────────────────────────┘
                               │ OpenFlow
┌──────────────────────────────┴──────────┐
│  container: sdn-controller              │
│  Os-Ken, port 6633                      │
└─────────────────────────────────────────┘
```

Containerul `topology` primește `CAP_NET_ADMIN`, `CAP_NET_RAW` și `CAP_SYS_ADMIN`
în `docker-compose.yml` — fără `sudo` pe host.

Accesul la namespace-urile h1/h2/h3 din `podman exec` se face prin comanda
`host <nume>` instalată în container, care folosește `nsenter` via `/proc/PID`.

---

## Structura fișierelor

```
sdn-podman/
├── controller/
│   ├── Dockerfile       # python:3.12-slim + os-ken==3.1.0
│   └── controller.py    # aplicația SDN (identică cu versiunea Mininet)
├── topology/
│   ├── Dockerfile       # ubuntu:24.04 + openvswitch-switch
│   └── entrypoint.sh    # pornește OVS, creează h1/h2/h3 intern, face wiring
├── scripts/
│   └── teardown.sh      # oprire curată
└── docker-compose.yml   # două servicii: controller + topology
```

---

## Cerințe

```bash
# Fedora / RHEL / Rocky
sudo dnf install -y podman podman-compose

# Ubuntu / Debian
sudo apt-get install -y podman podman-compose
```

---

## Pasul 1: curățarea sesiunilor anterioare

```bash
bash scripts/teardown.sh
```

---

## Pasul 2: construirea imaginilor

```bash
podman-compose build
```

---

## Pasul 3: pornirea lab-ului

```bash
podman-compose up -d
```

Verificați că ambele containere rulează:

```bash
podman ps --format "table {{.Names}}\t{{.Status}}"
```

Ieșire așteptată:

```
NAMES             STATUS
sdn-controller    Up X seconds
sdn-topology      Up X seconds
```

---

## Pasul 4: verificarea topologiei

Urmăriți log-urile containerului `topology` pentru a confirma că wiring-ul
intern s-a făcut și că OVS s-a conectat la controller:

```bash
podman logs sdn-topology
```

Ieșire așteptată:

```
[topo] OVS pornit.
[topo] Bridge s1 creat.
[topo] Configurez h1 (10.0.10.1/24, MAC 00:00:00:00:00:01, port OVS 1)...
[topo]   OK: h1 (PID=X) eth0=10.0.10.1/24 -> s1:port1
[topo] Configurez h2 ...
[topo] Configurez h3 ...
[topo] Conectez s1 la controller: tcp:controller:6633
```

Și în log-urile controllerului:

```bash
podman logs sdn-controller
```

Ar trebui să vedeți:

```
Table-miss flow instalat pe switch 1
```

---

## Oprirea lab-ului

```bash
bash scripts/teardown.sh
```

---

## Corespondență Mininet → Podman

| Mininet                            | Podman                                                           |
|------------------------------------|------------------------------------------------------------------|
| `sudo python3 topo_switch.py`      | `podman-compose up -d`                                           |
| `osken-manager controller.py`      | pornit automat în `sdn-controller`                               |
| `h1 ping -c 3 10.0.10.2`          | `podman exec sdn-topology host h1 ping -c 3 10.0.10.2`          |
| `s1 ovs-ofctl dump-flows s1`       | `podman exec sdn-topology ovs-ofctl -O OpenFlow13 dump-flows s1` |
| `xterm h1`                         | `podman exec -it sdn-topology host h1 bash`                      |
| `exit` (CLI Mininet)               | `bash scripts/teardown.sh`                                       |
