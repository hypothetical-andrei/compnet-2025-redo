# Sarcini: Topologia SDN cu Os-Ken și OVS în Podman

---

## 0. Pregătire: verificați modulul kernel OVS

Înainte de orice, verificați că modulul `openvswitch` este disponibil pe host:

```bash
lsmod | grep openvswitch
```

Dacă nu apare nimic:

```bash
sudo modprobe openvswitch
```

---

## 1. Pornirea topologiei

```bash
podman compose up -d
```

Urmăriți inițializarea — este important ca OVS să se conecteze la controller:

```bash
# Logurile OVS (așteptați mesajul "s1 este gata")
podman logs -f s1

# Logurile controllerului (așteptați mesajul despre table-miss flow instalat)
podman logs -f controller
```

> ✅ Așteptat în logurile `s1`: `s1 este gata. Aștept controllerul să instaleze flow-uri...`
> ✅ Așteptat în logurile `controller`: `Table-miss flow instalat pe switch <dpid>`

---

## 2. Verificarea interfețelor

Verificați că h1, h2, h3 au primit adresele de date pe `eth1`:

```bash
podman exec -it h1 ip a
podman exec -it h2 ip a
podman exec -it h3 ip a
```

> ✅ Așteptat: fiecare container are `eth1` cu adresa `10.0.10.x/24`
> (eth0 este interfața de management pe 172.20.0.x — ignorați-o)

Verificați porturile OVS din containerul s1:

```bash
podman exec -it s1 ovs-vsctl show
podman exec -it s1 ovs-ofctl dump-ports-desc br0 -O OpenFlow13
```

> ✅ Așteptat: porturile `p-h1` (OF port 1), `p-h2` (OF port 2), `p-h3` (OF port 3)

---

## 3. Testarea conectivității cu ping

#### a) h1 → h2 (trebuie să meargă)

```bash
podman exec -it h1 ping -c 3 10.0.10.2
```

> ✅ Așteptat: 3 reply-uri ICMP.
> Primul pachet ajunge la controller (PacketIn), care instalează flow-urile bidirecționale.
> Pachetele următoare sunt tratate direct de OVS.

#### b) h1 → h3 (trebuie să fie blocat)

```bash
podman exec -it h1 ping -c 3 10.0.10.3
```

> ✅ Așteptat: timeout (100% packet loss).
> Controllerul instalează un flow drop pentru destinația 10.0.10.3.

---

## 4. Inspectarea flow table-ului

Din containerul s1:

```bash
podman exec -it s1 ovs-ofctl dump-flows br0 -O OpenFlow13
```

Analizați output-ul și identificați:

- **Regula table-miss** (prioritate 0): trimite orice pachet necunoscut la controller
  ```
  priority=0 actions=CONTROLLER:65535
  ```

- **Flow-uri pentru h1 ↔ h2** (prioritate 10): forward bidirecțional
  ```
  priority=10,ip,nw_src=10.0.10.1,nw_dst=10.0.10.2 actions=output:2
  priority=10,ip,nw_src=10.0.10.2,nw_dst=10.0.10.1 actions=output:1
  ```

- **Flow drop pentru h3** (prioritate 20): drop pentru orice destinație 10.0.10.3
  ```
  priority=20,ip,nw_dst=10.0.10.3 actions=drop
  ```

> ⚠️ Flow-urile pentru h1↔h2 și drop-ul pentru h3 apar **doar după** primul ping.
> Dacă nu ați făcut ping încă, veți vedea doar table-miss.

---

## 5. *Opțional*: captură de trafic

Porniți captura pe portul h1 din OVS:

```bash
podman exec -it s1 tcpdump -i p-h1 -n icmp
```

Într-un alt terminal, generați trafic:

```bash
podman exec -it h1 ping -c 3 10.0.10.2
```

Observați pachetele ICMP. Pentru traficul blocat spre h3, după instalarea flow-ului drop, pachetele **nu mai apar** pe interfața p-h3 — sunt oprite direct în OVS.

---

## 6. Debugging: ce verificați dacă ceva nu merge

**OVS nu se conectează la controller:**
```bash
podman exec -it s1 ovs-vsctl get-controller br0
# Trebuie să arate: tcp:controller:6633
podman exec -it s1 ovs-vsctl show
# Secțiunea Controller trebuie să aibă is_connected: true
```

**h1 nu poate ping h2 deloc (nici primul pachet):**
```bash
# Verificați că OVS are porturile adăugate corect
podman exec -it s1 ovs-ofctl dump-ports br0 -O OpenFlow13
# Verificați că eth1 este up pe hosturi
podman exec -it h1 ip link show eth1
```

**Logurile s1 se opresc la "Aștept containerele h1, h2, h3":**
- Containerele host nu au pornit suficient de repede; rulați `podman compose up -d` din nou

---

## 7. Curățare

```bash
podman compose down
```

> **Notă:** La `compose down`, perechile veth create de init-s1.sh sunt șterse automat
> odată cu containerele.

---

## Deliverabil

Creați fișierul `sdn_podman_output.txt` care să conțină:

- Output `podman logs controller` (primele conexiuni și table-miss)
- Output `podman exec -it h1 ping -c 3 10.0.10.2`
- Output `podman exec -it h1 ping -c 3 10.0.10.3`
- Output complet `ovs-ofctl dump-flows br0 -O OpenFlow13` după ambele ping-uri
- 5–7 propoziții în care explicați:
  - cum se vede în flow table că traficul h1 ↔ h2 este permis
  - cum se vede că traficul către h3 este blocat
  - ce rol are regula table-miss
  - de ce h3 este izolat prin politică SDN și nu prin topologie fizică
  - ce diferență structurală există față de varianta Mininet (unde rulau OVS și controllerul)
