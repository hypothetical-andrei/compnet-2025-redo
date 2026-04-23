# Sarcini: Topologia SDN cu Os-Ken și Podman

> Înainte de a începe, asigurați-vă că ați parcurs `2a_sdn_podman_setup.md`
> și că ambele containere rulează (`podman ps`).

Toate comenzile către hosturi folosesc `host <nume>` — un helper instalat în
containerul `sdn-topology` care intră în namespace-ul corect via `nsenter`.

---

## 1. Verificarea conectivității cu ping

#### a) h1 către h2 — trebuie să meargă

```bash
podman exec sdn-topology host h1 ping -c 3 10.0.10.2
```

Ieșire așteptată:

```
PING 10.0.10.2 (10.0.10.2): 56 data bytes
64 bytes from 10.0.10.2: icmp_seq=0 ttl=64 time=X.X ms
64 bytes from 10.0.10.2: icmp_seq=1 ttl=64 time=X.X ms
64 bytes from 10.0.10.2: icmp_seq=2 ttl=64 time=X.X ms
```

#### b) h1 către h3 — trebuie blocat

```bash
podman exec sdn-topology host h1 ping -c 3 10.0.10.3
```

Ieșire așteptată:

```
PING 10.0.10.3 (10.0.10.3): 56 data bytes
(timeout — niciun reply)
```

---

## 2. Inspectarea flow table-ului

```bash
podman exec sdn-topology ovs-ofctl -O OpenFlow13 dump-flows s1
```

Ieșire tipică după ping-uri:

```
 cookie=0x0, ..., priority=0,actions=CONTROLLER:65535
 cookie=0x0, ..., priority=20,ip,nw_dst=10.0.10.3,actions=drop
 cookie=0x0, ..., priority=10,ip,nw_src=10.0.10.1,nw_dst=10.0.10.2,actions=output:2
 cookie=0x0, ..., priority=10,ip,nw_src=10.0.10.2,nw_dst=10.0.10.1,actions=output:1
```

Analizați:
- **priority=0** — regula table-miss: trimite pachetul necunoscut la controller
- **priority=10** — flow-uri bidirecționale h1 ↔ h2 (permise)
- **priority=20** — flow drop pentru orice destinație `10.0.10.3` (h3 blocat)

---

## 3. Urmărirea logurilor controller Os-Ken

Într-un terminal separat:

```bash
podman logs -f sdn-controller
```

Rulați din nou ping-urile și observați evenimentele:

- `PacketIn: dpid=... eth_src=... eth_dst=...` — pachet necunoscut ajuns la controller
- `Permis: 10.0.10.1 -> 10.0.10.2 prin portul 2` — flow instalat pentru h1 ↔ h2
- `Blocat: trafic catre 10.0.10.3` — flow drop instalat pentru h3

Observați că după instalarea flow-urilor, ping-urile ulterioare nu mai generează
evenimente `PacketIn` — switch-ul le tratează direct.

---

## 4. *Opțional*: captură de trafic

Capturați din interiorul namespace-ului h1 — interfața `eth0` a hostului:

**Terminal 1:**

```bash
podman exec sdn-topology host h1 tcpdump -i eth0 -n icmp
```

**Terminal 2:**

```bash
podman exec sdn-topology host h1 ping -c 3 10.0.10.2
podman exec sdn-topology host h1 ping -c 3 10.0.10.3
```

Observați că pentru traficul blocat spre h3, după instalarea flow-ului de drop,
pachetele nu mai apar — switch-ul le aruncă înainte de a le trimite pe orice port.

---

## 5. Shell interactiv în hosturi

```bash
# Shell în namespace-ul h1 (echivalent xterm h1 din Mininet)
podman exec -it sdn-topology host h1 bash

# Shell general în containerul topology (acces la ovs-vsctl, ovs-ofctl etc.)
podman exec -it sdn-topology bash
```

---

## Deliverable

Creați fișierul `sdn_stage2_output.txt` care să conțină:

- output de la:
  - `podman exec sdn-topology host h1 ping -c 3 10.0.10.2`
  - `podman exec sdn-topology host h1 ping -c 3 10.0.10.3`
- output complet de la `podman exec sdn-topology ovs-ofctl -O OpenFlow13 dump-flows s1`
- 5–7 propoziții în care explicați:
  - cum se vede în flow table că traficul h1 ↔ h2 este permis
  - cum se vede că traficul către h3 este blocat
  - ce rol are regula table-miss (priority=0)
  - de ce h3 este izolat prin politică SDN și nu prin topologie fizică
  - ce diferență există între `PacketOut` și `FlowMod` în logurile Os-Ken

Fișierul va fi completat în Stage 3 cu teste pe servere/clienți Python.
