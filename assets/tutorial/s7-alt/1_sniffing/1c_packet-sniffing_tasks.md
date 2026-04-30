# Sarcini – Sniffer simplu de pachete IPv4 (Podman)

Scriptul `packet_sniffer.py` este **neschimbat** față de varianta Mininet.
Tot ce diferă sunt comenzile de rulare.

---

## Pregătire

Porniți topologia dacă nu rulează deja:

```bash
podman-compose up -d

```

---

## 1. Completați `parse_ipv4_header`

Deschideți fișierul `1_sniffing/1b_packet_sniffer.py` și implementați funcția marcată cu
`# >>> STUDENT TODO`:

```python
version_ihl = data[0]
version = version_ihl >> 4
ihl = (version_ihl & 0x0F) * 4
ttl, proto, src, dst = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
src_ip_str = ipv4_addr(src)
dst_ip_str = ipv4_addr(dst)
return src_ip_str, dst_ip_str, proto, ihl
```

Ștergeți sau comentați linia `raise NotImplementedError(...)` după implementare.

---

## 2. Porniți snifferul pe h2

```bash
podman exec -it h2 python3 /sem7/1_sniffing/1b_packet_sniffer.py eth0
```

---

## 3. Generați trafic

Într-un terminal separat, generați trafic de pe h1 spre h2:

```bash
# ICMP
podman exec -it h1 ping -c 10 10.0.10.2

# TCP (dacă aveți tcp_server pornit pe h2)
podman exec -d h2 python3 /sem7/5_mini-ids/tcp_server.py 5000
podman exec -it h1 python3 /sem7/5_mini-ids/tcp_client.py 10.0.10.2 5000
```

Observați liniile afișate de sniffer:

```text
[1] 10.0.10.1 -> 10.0.10.2  proto=ICMP
[2] 10.0.10.2 -> 10.0.10.1  proto=ICMP
...
```

---

## 4. Opriți snifferul și salvați logul

Opriți cu `Ctrl-C` după cel puțin 20 de pachete. Copiați output-ul în
`logs/sniffer_log.txt` (volumul `./logs` este acceibil și de pe host):

```bash
# Redirectați output-ul direct la rulare:
podman exec h2 python3 /sem7/1_sniffing/1b_packet_sniffer.py eth0 > ./logs/sniffer_log.txt
# (generați trafic din alt terminal, apoi Ctrl-C după 20+ pachete)
```

---

## 5. Întrebări de reflecție (de scris în `logs/sniffer_log.txt`)

1. Ce protocol ați văzut cel mai des în captură (ICMP, TCP, UDP)?
2. Ce adrese IP apar cel mai frecvent ca destinație? De ce?
3. Ce se întâmplă cu snifferul dacă nu aveți `CAP_NET_RAW` (fără privilegii suficiente)?

---

## Deliverabil

- `1_sniffing/1b_packet_sniffer.py` completat
- `logs/sniffer_log.txt` cu cel puțin 20 de linii + răspunsurile la întrebări
