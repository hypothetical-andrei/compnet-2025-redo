# Sarcini: Trafic TCP și UDP prin switch-ul SDN

Aceste sarcini continuă peste Stage 2 (controller Os-Ken + topologie SDN cu Podman).

Presupunem că:
- `podman-compose up -d` a fost rulat
- ambele containere sunt active (`podman ps`)
- ping h1 → h2 funcționează (verificat în Stage 2)

---

## 1. Test TCP permis între h1 și h2

Porniți serverul TCP pe h2 în background:

```bash
podman exec sdn-topology bg h2 tcp-server python3 /apps/tcp_server.py 5000
```

Porniți clientul TCP pe h1 (interactiv):

```bash
podman exec -it sdn-topology host h1 python3 /apps/tcp_client.py 10.0.10.2 5000
```

Trimiteți câteva mesaje (ex: `hello`, `test`) și verificați că serverul le afișează
și clientul primește ecou. Opriți clientul cu `exit`.

Verificați log-ul serverului:

```bash
podman exec sdn-topology cat /var/log/bg-h2-tcp-server.log
```

Opriți serverul:

```bash
podman exec sdn-topology bg-stop h2 tcp-server
```

---

## 2. Test TCP blocat între h1 și h3

> Nu este nevoie de niciun server pe h3 — traficul este blocat de controller
> înainte să ajungă la destinație.

Încercați să vă conectați de pe h1 la h3:

```bash
podman exec -it sdn-topology host h1 python3 /apps/tcp_client.py 10.0.10.3 5000
```

Ar trebui să vedeți `Connection failed` sau timeout.

Verificați log-ul controllerului:

```bash
podman logs sdn-controller | tail -20
```

Inspectați flow table-ul:

```bash
podman exec sdn-topology ovs-ofctl -O OpenFlow13 dump-flows s1
```

Ar trebui să apară flow-ul de tip drop pentru TCP către 10.0.10.3.

---

## 3. Test UDP spre h3 cu controllerul inițial

Porniți serverul UDP pe h3:

```bash
podman exec sdn-topology bg h3 udp-server python3 /apps/udp_server.py 6000
```

Porniți clientul UDP pe h1:

```bash
podman exec -it sdn-topology host h1 python3 /apps/udp_client.py 10.0.10.3 6000
```

> ❌ Așteptat: mesajele nu ajung la server. Controllerul inițial blochează
> orice trafic IP către 10.0.10.3, indiferent de protocol.

Opriți serverul UDP:

```bash
podman exec sdn-topology bg-stop h3 udp-server
```

---

## 4. Modificarea controllerului: permite UDP, blochează TCP spre h3

Controllerul din acest stage are deja logica modificată — tratează TCP și UDP
spre h3 separat. Trebuie doar să îl reporniți și să ștergeți flow-urile vechi.

Reconstruiți și reporniți containerul controller:

```bash
podman rm -f sdn-controller
podman rmi 2_sdn_controller --force
podman-compose build --no-cache controller
podman-compose up -d
```

Ștergeți flow-urile vechi din switch (altfel flow-ul de drop general pentru
10.0.10.3 rămâne activ):

```bash
podman exec sdn-topology ovs-ofctl -O OpenFlow13 del-flows s1
```

> ⚠️ După `del-flows`, switch-ul nu mai are nicio regulă — inclusiv table-miss
> dispare. Controllerul o va reinstala automat la prima reconectare.
> Verificați cu `podman logs sdn-controller | tail -5` că apare
> `Table-miss flow instalat pe switch`.

---

## 5. Retestare UDP și TCP spre h3

Porniți din nou serverul UDP pe h3:

```bash
podman exec sdn-topology bg h3 udp-server python3 /apps/udp_server.py 6000
```

Testați clientul UDP de pe h1:

```bash
podman exec -it sdn-topology host h1 python3 /apps/udp_client.py 10.0.10.3 6000
```

> ✅ Așteptat: mesajele ajung la server și primiți ecou — UDP este acum permis.

Testați clientul TCP de pe h1:

```bash
podman exec -it sdn-topology host h1 python3 /apps/tcp_client.py 10.0.10.3 5000
```

> ❌ Așteptat: conexiunea eșuează — TCP spre h3 rămâne blocat.

Opriți serverul UDP:

```bash
podman exec sdn-topology bg-stop h3 udp-server
```

---

## 6. Inspectarea flow-urilor după modificare

```bash
podman exec sdn-topology ovs-ofctl -O OpenFlow13 dump-flows s1
```

Căutați:
- flow cu `ip_proto=17,nw_dst=10.0.10.3` și acțiune `output:3` (UDP permis)
- flow cu `ip_proto=6,nw_dst=10.0.10.3` și acțiuni goale (TCP drop)

---

## Deliverable final SDN

Combinați toate rezultatele din Stage 2 și Stage 3 într-un singur fișier
`sdn_lab_output.txt` care să conțină:

**Din Stage 2:**
- `podman exec sdn-topology host h1 ping -c 3 10.0.10.2` (reușit)
- `podman exec sdn-topology host h1 ping -c 3 10.0.10.3` (eșuat)
- `podman exec sdn-topology ovs-ofctl -O OpenFlow13 dump-flows s1` (flow table inițial)

**Din Stage 3:**
- output client TCP h1 → h2 (reușit)
- output client TCP h1 → h3 (eșuat)
- output client UDP h1 → h3 (eșuat înainte de modificare, reușit după)
- `podman exec sdn-topology ovs-ofctl -O OpenFlow13 dump-flows s1` (după modificare)

**O explicație de 8–10 propoziții** în care descrieți:
- diferența dintre rutare clasică și SDN
- cum influențează controllerul Os-Ken traficul TCP și UDP
- cum se vede în flow table politica de securitate (blocare TCP, permitere UDP)
- ce avantaje are SDN pentru politici fine (application-aware)

Acest fișier va fi tema de predat pentru Seminarul 6.
