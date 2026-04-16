# Sarcini – Mini IDS integrat (Podman)

Scriptul `mini_ids.py` combină sniffing RAW, detectare port scan TCP, UDP spray
și flood. Alertele sunt scrise în `/logs/ids_alerts.log` (accesibil pe host în `./logs/`).

---

## 1. Verificați și completați `log_alert`

Funcția este deja implementată în script. Verificați că:
- construiește mesajul cu timestamp (`time.strftime`)
- îl afișează pe ecran
- îl scrie în `/logs/ids_alerts.log` în modul append (`"a"`)

---

## 2. Porniți mini IDS pe h2

```bash
podman exec -it h2 python3 /apps/mini_ids.py eth1
```

Lăsați-l să ruleze pe tot parcursul scenariilor de mai jos.

---

## 3. Scenariu 1 — Port scan TCP

Din h1, lansați scanner-ul:

```bash
podman exec -it h1 python3 /apps/port_scanner.py 10.0.10.2 1 200
```

> ✅ Așteptat în IDS:
> ```
> [2025-...] Posibil TCP PORT SCAN de la 10.0.10.1: 10 porturi SYN in ultimele 5s
> ```

---

## 4. Scenariu 2 — UDP spray

Folosiți scriptul helper `udp_spray.py` de pe h1:

```bash
podman exec -it h1 python3 /apps/udp_spray.py 10.0.10.2 6000 6030
```

> ✅ Așteptat în IDS:
> ```
> [2025-...] Posibil UDP SPRAY de la 10.0.10.1: 10 porturi UDP in ultimele 5s
> ```

> **Notă:** `udp_spray.py` trimite câte un pachet UDP spre fiecare port din intervalul dat,
> cu o pauză de 50ms între pachete. Ajustați intervalul dacă alerta nu apare
> (trebuie minim `UDP_PORT_THRESHOLD` porturi distincte în `WINDOW_SECONDS` secunde).

---

## 5. Scenariu 3 — Flood TCP spre un port

Porniți serverul TCP pe h2 (dacă nu rulează):

```bash
podman exec -d h2 python3 /apps/tcp_server.py 5000
```

De pe h1, generați multe conexiuni rapide spre portul 5000:

```bash
podman exec -it h1 python3 -c "
import socket, time
for i in range(60):
    try:
        s = socket.socket()
        s.settimeout(0.3)
        s.connect(('10.0.10.2', 5000))
        s.close()
    except:
        pass
    time.sleep(0.05)
print('done')
"
```

> ✅ Așteptat în IDS:
> ```
> [2025-...] Posibil TCP FLOOD catre 10.0.10.2:5000 (50 pachete in ultimele 5s)
> ```

Opriți serverul:

```bash
podman exec h2 pkill -f tcp_server.py
```

---

## 6. Verificați `logs/ids_alerts.log`

```bash
cat ./logs/ids_alerts.log
```

Verificați că sunt înregistrate alerte pentru toate cele 3 scenarii.

---

## 7. Raport — `logs/explanation.md`

Scrieți 10–15 propoziții (sau 3–5 paragrafe) despre:

1. **Ce tipuri de comportamente detectează mini IDS-ul:**
   - port scan TCP (multi-port SYN fără ACK)
   - UDP spray (multi-port UDP de la aceeași sursă)
   - flood TCP spre un port specific

2. **Ce parametri controlează sensibilitatea:**
   - `WINDOW_SECONDS`, `TCP_SYN_THRESHOLD`, `UDP_PORT_THRESHOLD`, `FLOOD_THRESHOLD`

3. **Exemple de false positive și false negative:**
   - când ați putea avea alertă fără atac real
   - când un atac real ar trece neobservat

4. **Cel puțin 2 idei de îmbunătățire:**
   - scan lent (pachete la intervale mari, sub pragul ferestrei)
   - analiză pe conținut (semnături), integrare cu log centralizat etc.

---

## 8. Curățare

```bash
podman exec h2 pkill -f mini_ids.py 2>/dev/null || true
podman exec h2 pkill -f tcp_server.py 2>/dev/null || true
podman compose down
```

---

## Deliverabil final Seminar 7

Predați un pachet care conține:

| Fișier | Provenit din |
|--------|-------------|
| `apps/packet_sniffer.py` | Stage 2, completat |
| `apps/packet_filter.py` | Stage 3, completat |
| `apps/port_scanner.py` | Stage 4, completat |
| `apps/detect_scan.py` | Stage 5 |
| `apps/mini_ids.py` | Stage 6, completat |
| `logs/sniffer_log.txt` | Stage 2 |
| `logs/filter_results.txt` | Stage 3 |
| `logs/scan_results.txt` | Stage 4 |
| `logs/scan_detection.txt` | Stage 5 |
| `logs/ids_alerts.log` | Stage 6 |
| `logs/explanation.md` | Stage 6 |
