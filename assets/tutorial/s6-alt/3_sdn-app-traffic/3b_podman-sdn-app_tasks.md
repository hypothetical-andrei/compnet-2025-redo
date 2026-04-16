# Sarcini: Trafic TCP și UDP prin switch-ul SDN (Podman)

Aceste sarcini continuă peste Stage 2. Presupunem că:

- topologia Podman este pornită (`podman compose up -d`)
- OVS este conectat la controller (verificați cu `podman logs s1` și `podman logs controller`)

---

## 1. Test TCP permis: h1 → h2

Porniți serverul TCP pe h2 în background:

```bash
podman exec -d h2 python3 /apps/tcp_server.py 5000
```

Porniți clientul TCP pe h1 (interactiv):

```bash
podman exec -it h1 python3 /apps/tcp_client.py 10.0.10.2 5000
```

Trimiteți câteva mesaje (ex: `hello`, `test`) și verificați că serverul le afișează
și clientul primește ecou. Opriți clientul cu `exit`, apoi opriți serverul:

```bash
podman exec h2 pkill -f tcp_server.py
```

---

## 2. Test TCP blocat: h1 → h3

> ℹ️ Nu este nevoie de niciun server pe h3 — traficul este blocat de controller
> înainte să ajungă la destinație.

```bash
podman exec -it h1 python3 /apps/tcp_client.py 10.0.10.3 5000
```

> ❌ Așteptat: `Connection failed` sau timeout.

Verificați logurile controllerului pentru mesajul de blocare:

```bash
podman logs controller | grep -i blocat
```

Inspectați flow table-ul:

```bash
podman exec -it s1 ovs-ofctl dump-flows br0 -O OpenFlow13
```

> ✅ Așteptat: un flow cu `ip_proto=6, nw_dst=10.0.10.3` și `actions=drop`.

---

## 3. Test UDP spre h3 înainte de modificarea controllerului

Porniți serverul UDP pe h3 în background:

```bash
podman exec -d h3 python3 /apps/udp_server.py 6000
```

Porniți clientul UDP pe h1:

```bash
podman exec -it h1 python3 /apps/udp_client.py 10.0.10.3 6000
```

> ❌ Așteptat: mesajele nu ajung la server (nu primiți ecou, timeout la recvfrom).
>
> Dacă în Stage 2 a fost instalat un flow de drop general pentru `nw_dst=10.0.10.3`
> (fără `ip_proto`), acesta blochează și UDP. Dacă folosiți controllerul deja actualizat
> (NEW), flow-ul de drop este specific TCP (`ip_proto=6`) și UDP poate fi deja permis —
> în acest caz săriți la Task 5.

Opriți serverul UDP:

```bash
podman exec h3 pkill -f udp_server.py
```

---

## 4. Actualizarea controllerului și ștergerea flow-urilor vechi

Controllerul din `controller/sdn_controller.py` este deja versiunea actualizată (NEW):
UDP spre h3 este permis, TCP spre h3 rămâne blocat. Nu este nevoie de modificări
în cod — dar trebuie să resetați starea OVS și să reporniți controllerul.

### Pasul 1 — Ștergeți flow-urile vechi din OVS

```bash
podman exec -it s1 ovs-ofctl del-flows br0 -O OpenFlow13
```

> ⚠️ Aceasta șterge **toate** flow-urile, inclusiv table-miss.
> Controllerul le va reinstala automat la reconectare.

### Pasul 2 — Reporniți controllerul

```bash
podman restart controller
```

### Pasul 3 — Verificați reconectarea

```bash
podman logs controller | tail -20
```

> ✅ Așteptat: `Table-miss flow instalat pe switch <dpid>` (semn că OVS s-a reconectat).

Dacă table-miss nu apare în câteva secunde, forțați reconectarea OVS:

```bash
podman exec -it s1 ovs-vsctl del-controller br0
podman exec -it s1 ovs-vsctl set-controller br0 tcp:controller:6633
```

---

## 5. Retestare UDP și TCP spre h3

### UDP (trebuie să meargă acum)

Porniți serverul UDP pe h3:

```bash
podman exec -d h3 python3 /apps/udp_server.py 6000
```

Porniți clientul UDP pe h1:

```bash
podman exec -it h1 python3 /apps/udp_client.py 10.0.10.3 6000
```

> ✅ Așteptat: mesajele ajung la server și primiți ecou.

Verificați logurile controllerului:

```bash
podman logs controller | grep -i "permis UDP"
```

### TCP (trebuie să rămână blocat)

```bash
podman exec -it h1 python3 /apps/tcp_client.py 10.0.10.3 5000
```

> ❌ Așteptat: `Connection failed`.

Opriți serverul UDP:

```bash
podman exec h3 pkill -f udp_server.py
```

---

## 6. Inspectarea flow-urilor după modificare

```bash
podman exec -it s1 ovs-ofctl dump-flows br0 -O OpenFlow13
```

Identificați în output:

- **table-miss** (prioritate 0): `actions=CONTROLLER:65535`
- **UDP permis spre h3** (prioritate 20): `ip,ip_proto=17,nw_dst=10.0.10.3 actions=output:3`
- **TCP drop spre h3** (prioritate 20): `ip,ip_proto=6,nw_dst=10.0.10.3 actions=drop`
- **h1 ↔ h2 permis** (prioritate 10): cele două flow-uri bidirecționale

---

## 7. Curățare

```bash
podman exec h3 pkill -f udp_server.py 2>/dev/null || true
podman exec h2 pkill -f tcp_server.py 2>/dev/null || true
podman compose down
```

---

## Deliverabil final SDN

Combinați toate rezultatele din Stage 2 și Stage 3 într-un singur fișier `sdn_lab_output.txt`:

**Din Stage 2:**
- `podman exec -it h1 ping -c 3 10.0.10.2` (reușit)
- `podman exec -it h1 ping -c 3 10.0.10.3` (eșuat)
- `ovs-ofctl dump-flows br0` — flow table inițial

**Din Stage 3:**
- output client TCP h1 → h2 (reușit)
- output client TCP h1 → h3 (eșuat)
- output client UDP h1 → h3 (eșuat înainte de resetare, reușit după)
- `ovs-ofctl dump-flows br0` după resetare și retestare

**O explicație de 8–10 propoziții** în care descrieți:
- diferența dintre rutare clasică (topologia triunghi din Stage 1) și SDN
- cum influențează controllerul Os-Ken traficul TCP și UDP în mod diferit
- cum se vede în flow table politica de securitate (blocare TCP, permitere UDP)
- ce avantaje are SDN pentru politici fine la nivel de aplicație (application-aware)
- ce diferență operațională ați observat față de varianta Mininet (CLI vs `podman exec`)

Acest fișier va fi tema de predat pentru Seminarul 6.
