# Sarcini – Detectarea unui port scan (Podman)

Scriptul `detect_scan.py` folosește `AF_PACKET` și necesită `CAP_NET_RAW` —
deja configurat în `compose.yaml` pentru toate containerele host.

Scenariul: **h1 = scanner (atacator), h2 = victimă (detector activ)**.

---

## 1. Pregătirea mediului

Verificați că topologia rulează și că h1/h2 au adresele de date pe `eth0`:

```bash
podman exec -it h1 ip a show eth0   # 10.0.10.1/24
podman exec -it h2 ip a show eth0   # 10.0.10.2/24
```

---

## 2. Porniți `detect_scan` pe h2

```bash
podman exec -it h2 python3 /sem7/4_scan-detector/4a_detect-scan.py eth0
```

---

## 3. Rulați `port_scanner` de pe h1

Într-un terminal separat:

```bash
podman exec -it h1 python3 /sem7/3_port-scanning/3a_port_scanner.py 10.0.10.2 1 200
```

Pe măsură ce scanner-ul încearcă conexiuni TCP spre h2, `detect_scan` va vedea
pachetele SYN și va afișa:

```text
[ALERT] Posibil port scan de la 10.0.10.1: 10 porturi diferite in ultimele 5 secunde
```

---

## 4. Ajustați sensibilitatea

În `4_scan-detector/4a_detect-scan.py`, modificați:

```python
WINDOW_SECONDS = 2
PORT_THRESHOLD = 5
```

Repetați testul. Observați:
- Apare alerta mai repede?
- Există riscul de false positive cu trafic normal?

---

## 5. Test cu trafic normal (fără scanner)

Generați trafic obișnuit de pe h1:

```bash
podman exec -it h1 ping -c 5 10.0.10.2
podman exec -d h2 python3 /sem7/5_mini-ids/tcp_server.py 5000
podman exec -it h1 python3 /sem7/5_mini-ids/tcp_client.py 10.0.10.2 5000
# trimiteți 3-4 mesaje, apoi exit
```

Observați dacă `detect_scan` se declanșează pentru trafic normal spre un singur port.

---

## 6. Deliverabil

Creați `logs/scan_detection.txt` (copiați manual output-ul din terminal):

1. Fragment din `detect_scan` în timpul scanării — cu cel puțin o linie `[ALERT]`
2. Fragment din `detect_scan` în timpul traficului normal — fără alertă
3. Rezumat de 6–8 propoziții:
   - ce condiție folosește scriptul pentru a decide că are loc un port scan
   - cum influențează `WINDOW_SECONDS` și `PORT_THRESHOLD` sensibilitatea
   - ce tip de fals pozitiv ați putea avea
   - cum ar putea fi îmbunătățit detectorul
