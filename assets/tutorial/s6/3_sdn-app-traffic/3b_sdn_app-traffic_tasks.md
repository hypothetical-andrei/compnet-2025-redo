# Sarcini: Trafic TCP și UDP prin switch-ul SDN

Aceste sarcini continuă peste Stage 2 (controller Os-Ken + topologie SDN).

Presupunem că:
- controllerul Os-Ken este pornit cu `osken-manager index_sdn_os-ken_controller.py`
- topologia Mininet SDN este pornită cu `sudo python3 index_sdn_topo_switch.py`

---

## 1. Test TCP permis între h1 și h2

Porniți serverul TCP pe h2 în background:

```
h2 python3 tcp_server.py 5000 &
```

Porniți clientul TCP pe h1:

```
h1 python3 tcp_client.py 10.0.10.2 5000
```

Trimiteți câteva mesaje (ex: `hello`, `test`) și verificați că serverul le afișează și clientul primește ecou.

Opriți clientul cu `exit`, apoi opriți serverul:

```
h2 pkill -f tcp_server.py
```

---

## 2. Test TCP blocat între h1 și h3

> ℹ️ Nu este nevoie de niciun server pe h3 — traficul este blocat de controller înainte să ajungă la destinație.

Încercați să vă conectați de pe h1 la h3:

```
h1 python3 tcp_client.py 10.0.10.3 5000
```

Ar trebui să vedeți `Connection failed` sau timeout. Verificați în log-ul Os-Ken mesajele despre drop pentru trafic către 10.0.10.3, și inspectați flow table-ul:

```bash
sudo ovs-ofctl dump-flows s1
```

Ar trebui să apară flow-ul de tip drop instalat de controller.

---

## 3. Test UDP spre h3 (blocat de flow-ul existent)

Porniți serverul UDP pe h3 în background:

```
h3 python3 udp_server.py 6000 &
```

Porniți clientul UDP pe h1:

```
h1 python3 udp_client.py 10.0.10.3 6000
```

> ❌ Așteptat: mesajele nu ajung la server. Flow-ul de drop instalat în task 2 blochează orice trafic IP către 10.0.10.3, indiferent de protocol (TCP sau UDP).

Opriți serverul UDP:

```
h3 pkill -f udp_server.py
```

---

## 4. Modificare controller Os-Ken: permite UDP, blochează TCP spre h3

În fișierul `index_sdn_os-ken_controller.py`, înlocuiți blocul care tratează `dst_ip == "10.0.10.3"` cu logică separată pe protocol:

```python
if dst_ip == "10.0.10.3":
    proto = ipv4_pkt.proto  # 6 = TCP, 17 = UDP

    if proto == 6:
        # TCP spre h3 -> drop
        match = parser.OFPMatch(
            eth_type=0x0800,
            ip_proto=6,
            ipv4_dst=dst_ip
        )
        actions = []  # lista goala = drop
        self.logger.info("Blocat TCP catre %s", dst_ip)

    elif proto == 17:
        # UDP spre h3 -> permis, trimitem pe portul 3 (h3)
        match = parser.OFPMatch(
            eth_type=0x0800,
            ip_proto=17,
            ipv4_dst=dst_ip
        )
        actions = [parser.OFPActionOutput(3)]
        self.logger.info("Permis UDP catre %s", dst_ip)

    else:
        return  # alt protocol, ignoram

    self.add_flow(
        datapath,
        priority=20,
        match=match,
        actions=actions,
        buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
    )
    return
```

După modificare, reporniți controllerul (într-un terminal separat):

```bash
osken-manager index_sdn_os-ken_controller.py
```

Și ștergeți flow-urile vechi din switch (altfel flow-ul de drop general pentru 10.0.10.3 rămâne activ):

```bash
sudo ovs-ofctl del-flows s1
```

> ⚠️ După `del-flows`, switch-ul nu mai are nicio regulă — inclusiv table-miss dispare. Controllerul o va reinstala automat când se reconectează, dar dacă nu o face imediat, reporniți și topologia Mininet.

---

## 5. Retestare UDP și TCP spre h3

Porniți din nou serverul UDP pe h3:

```
h3 python3 udp_server.py 6000 &
```

Testați clientul UDP de pe h1:

```
h1 python3 udp_client.py 10.0.10.3 6000
```

> ✅ Așteptat: mesajele ajung la server și primiți ecou — UDP este acum permis.

Testați clientul TCP de pe h1:

```
h1 python3 tcp_client.py 10.0.10.3 5000
```

> ❌ Așteptat: conexiunea eșuează — TCP spre h3 rămâne blocat.

Opriți serverul UDP:

```
h3 pkill -f udp_server.py
```

---

## 6. Inspectarea flow-urilor după modificare

```bash
sudo ovs-ofctl dump-flows s1
```

Căutați:
- flow cu `ip_proto=17, nw_dst=10.0.10.3` și acțiune `output:3` (UDP permis)
- flow cu `ip_proto=6, nw_dst=10.0.10.3` și acțiuni goale (TCP drop)

---

## Deliverable final SDN

Combinați toate rezultatele din Stage 2 și Stage 3 într-un singur fișier `sdn_lab_output.txt` care să conțină:

**Din Stage 2:**
- ping h1 → h2 (reușit)
- ping h1 → h3 (eșuat)
- dump flow table inițial

**Din Stage 3:**
- output client TCP h1 → h2 (reușit)
- output client TCP h1 → h3 (eșuat)
- output client UDP h1 → h3 (eșuat înainte de modificare, reușit după)
- dump flow table după modificarea controllerului

**O explicație de 8–10 propoziții** în care descrieți:
- diferența dintre rutare clasică (triangle) și SDN
- cum influențează controllerul Os-Ken traficul TCP și UDP
- cum se vede în flow table politica de securitate (blocare TCP, permitere UDP)
- ce avantaje are SDN pentru astfel de politici fine (application-aware)

Acest fișier va fi tema de predat pentru Seminarul 6.