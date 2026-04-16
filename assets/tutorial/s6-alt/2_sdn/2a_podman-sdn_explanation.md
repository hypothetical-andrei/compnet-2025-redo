# Introducere SDN cu Podman Compose: switch OpenFlow și controller Os-Ken

În această secțiune vom recrea topologia SDN folosind **Podman Compose**. Vom avea un switch Open vSwitch (OVS) rulând într-un container dedicat, un controller Os-Ken într-un container separat, și trei hosturi ca containere individuale. Scopul este același: să observăm cum controllerul impune o politică de rețea prin flow-uri OpenFlow.

---

## Concept de bază SDN (neschimbat față de Mininet)

Software Defined Networking separă:

- **control plane** — logica de decizie (controllerul Os-Ken)
- **data plane** — dispozitivul care aplică regulile (switch-ul OVS)

Controllerul vorbește cu switch-ul prin protocolul **OpenFlow 1.3** pe portul TCP **6633**.

---

## Topologia

```
h1 ---- s1 ---- h2
         |
        h3
        
[controller Os-Ken] <--OpenFlow TCP 6633--> [s1 OVS]
```

Toate containerele rulează în aceeași rețea de management (`net_mgmt`) prin care OVS se conectează la controller. Hosturile sunt conectate la OVS prin rețele bridge dedicate, iar OVS le adaugă ca porturi interne.

---

## Arhitectura Podman vs. Mininet

| Componentă Mininet | Echivalent Podman |
|---|---|
| `OVSSwitch s1` | Container `s1` cu `openvswitch` instalat |
| `RemoteController c0` | Container `controller` cu `os-ken` instalat |
| `h1`, `h2`, `h3` (hosturi Mininet) | Containere `h1`, `h2`, `h3` (`nicolaka/netshoot`) |
| Linkuri `addLink(h1, s1)` | Interfețe veth conectate la OVS prin `ovs-vsctl add-port` |
| `autoSetMacs=True` | MAC-uri setate manual în scriptul de init al OVS |

---

## De ce avem nevoie de un container dedicat pentru OVS

În Mininet, OVS rulează direct pe host-ul Linux și are acces la kernel-ul sistemului (modulele `openvswitch`). În Podman, îl rulăm într-un **container privilegiat** care accesează modulele kernel ale host-ului. Containerul OVS:

- pornește daemonii `ovsdb-server` și `ovs-vswitchd`
- creează bridge-ul `br0`
- adaugă perechi veth pentru fiecare host (câte un capăt în container-ul host, celălalt în OVS)
- se conectează la controller prin TCP pe rețeaua de management

> **Cerință host:** modulul kernel `openvswitch` trebuie să fie disponibil.
> Verificați cu: `lsmod | grep openvswitch`
> Dacă nu este încărcat: `sudo modprobe openvswitch`

---

## Schema de adresare

| Host | MAC (fix) | Adresă IPv4 |
|------|-----------|-------------|
| h1 | 00:00:00:00:00:01 | 10.0.10.1/24 |
| h2 | 00:00:00:00:00:02 | 10.0.10.2/24 |
| h3 | 00:00:00:00:00:03 | 10.0.10.3/24 |

MAC-urile sunt fixate manual pentru a păstra compatibilitatea cu logica din controller (`H1_MAC`, `H2_MAC`, `H3_MAC`).

---

## Cum funcționează conectivitatea h1/h2/h3 ↔ OVS

Fiecare host este conectat la OVS printr-o **pereche veth** creată de scriptul de inițializare:

```
[h1: eth1 / 10.0.10.1] <--veth--> [s1: port "p-h1" în br0, OF port 1]
[h2: eth1 / 10.0.10.2] <--veth--> [s1: port "p-h2" în br0, OF port 2]
[h3: eth1 / 10.0.10.3] <--veth--> [s1: port "p-h3" în br0, OF port 3]
```

Ordinea adăugării porturilor în OVS determină numerele de port OpenFlow (port 1 = h1, port 2 = h2, port 3 = h3), exact ca în Mininet.

> **Notă:** Containerele host au două interfețe: `eth0` (rețeaua de management, pentru `podman exec`) și `eth1` (interfața de date, conectată la OVS). Adresele `10.0.10.x` sunt pe `eth1`.

---

## Comportamentul politicii SDN (identic cu Mininet)

- **h1 ↔ h2**: permis — controllerul instalează flow-uri bidirecționale la primul pachet
- **orice → h3**: blocat — controllerul instalează un flow drop cu prioritate 20

---

## Structura fișierelor

```
./
├── compose.yaml
├── scripts/
│   └── init-s1.sh           # pornire OVS, creare bridge, conectare porturi veth
└── controller/
    └── sdn_controller.py    # aplicația Os-Ken (identică cu varianta Mininet)
```

---

## Cum se pornește topologia

```bash
# Verificați că modulul OVS e disponibil pe host
lsmod | grep openvswitch || sudo modprobe openvswitch

# Porniți topologia
podman compose up -d

# Verificați că OVS s-a conectat la controller
podman logs s1
podman logs controller

# Accesați containerele
podman exec -it h1 bash
podman exec -it s1 bash

# Opriți
podman compose down
```

---

## Obiectivele studentului

- să pornească topologia și să verifice conectarea OVS la controller (din loguri)
- să testeze conectivitatea: `h1 ping h2` trebuie să meargă, `h1 ping h3` trebuie blocat
- să inspecteze flow table-ul OVS cu `ovs-ofctl dump-flows br0` din containerul `s1`
- să identifice în flow table: regula table-miss, flow-urile pentru h1↔h2, flow-ul drop pentru h3

Completați toate sarcinile din fișierul `2d_podman-sdn_tasks.md`.
