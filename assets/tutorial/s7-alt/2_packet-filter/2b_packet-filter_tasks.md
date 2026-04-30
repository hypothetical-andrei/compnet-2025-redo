# Sarcini – Filtru de pachete TCP/UDP (Podman)

Scriptul `packet_filter.py` este **neschimbat**. Adaptările sunt doar în comenzi.

---

## 1. Copiați implementarea `parse_ipv4_header`

Dacă nu ați făcut-o deja, implementați funcția în `2_packet-filter/2a_packet-filter.py`
(aceea din `packet_sniffer.py` funcționează identic):

```python
version_ihl = data[0]
ihl = (version_ihl & 0x0F) * 4
ttl, proto, src, dst = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
return ipv4_addr(src), ipv4_addr(dst), proto, ihl
```

---

## 2. Filtrul – Pasul 1 (numai TCP)

În `passes_filter`, implementați:

```python
if proto == 6:
    return True
return False
```

Rulați filtrul pe h2 și generați trafic TCP de pe h1:

```bash
# Terminal 1 — filtrul
podman exec -it h2 python3 /sem7/2_packet-filter/2a_packet-filter.py eth0

# Terminal 2 — trafic TCP
podman exec -d h2 python3 /sem7/5_mini-ids/tcp_server.py 5000
podman exec -it h1 python3 /sem7/5_mini-ids/tcp_client.py 10.0.10.2 5000
```

Verificați că vedeți doar linii cu `proto=TCP`.

---

## 3. Filtrul – Pasul 2 (UDP port 53 + TCP port > 1024)

```python
if proto == 17 and dst_port == 53:
    return True
if proto == 6 and dst_port is not None and dst_port > 1024:
    return True
return False
```

Pentru a genera trafic UDP/53, pornim un server UDP pe h2 la portul 53 și trimitem
de pe h1 — simulăm trafic de tip DNS fără să avem nevoie de internet:

```bash
# Terminal 1 — filtrul pe h2
podman exec -it h2 python3 /sem7/2_packet-filter/2a_packet-filter.py eth0

# Terminal 2 — server UDP pe portul 53
podman exec -d h2 python3 /sem7/5_mini-ids/udp_server.py 53

# Terminal 3 — client UDP trimite spre portul 53
podman exec -it h1 python3 /sem7/5_mini-ids/udp_client.py 10.0.10.2 53
```

Verificați că filtrul afișează linii `proto=UDP` cu `dst_port=53` și linii
`proto=TCP` cu `dst_port > 1024`.

---

## 4. Filtrul – Pasul 3 (filtru pe sursa IP)

Adăugați restricție pe prefixul sursei:

```python
if not src_ip.startswith("10."):
    return False
# ... restul regulilor
```

În această topologie, sursele pe `eth0` vor fi din `10.0.10.0/24`.

---

## 5. Rulați și colectați rezultate

```bash
podman exec h2 python3 /sem7/2_packet-filter/2a_packet-filter.py eth0 > ./logs/filter_results.txt
```

Generați trafic mixt (ICMP, TCP, UDP) și verificați că filtrul elimină ce nu trebuie.

---

## 6. Întrebări de reflecție (în `logs/filter_results.txt`)

1. Ce tip de trafic ați reușit să filtrați cel mai ușor (TCP/UDP)?
2. De ce filtrarea pe port destinație poate fi înșelătoare în practică?
3. Ce ați schimba dacă ați dori să detectați doar traficul DNS real (către 8.8.8.8)?

---

## Deliverabil

- `2_packet-filter/2a_packet-filter.py` completat (cu `passes_filter` implementată)
- `logs/filter_results.txt` cu minimum 20 de linii + răspunsuri
