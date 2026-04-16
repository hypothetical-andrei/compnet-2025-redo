# Sarcini – Mini port-scanner TCP (Podman)

Scriptul `port_scanner.py` este **neschimbat** și nu necesită privilegii de root —
nu folosește socket-uri RAW. Rezultatele sunt salvate în `/logs/scan_results.txt`
(accesibil de pe host în `./logs/`).

---

## 1. Completați funcțiile `scan_port` și `scan_range`

Implementarea propusă în script este deja completă — verificați că înțelegeți:

- `scan_port`: încearcă `connect()`, returnează `"OPEN"` / `"CLOSED"` / `"FILTERED"`
- `scan_range`: iterează porturile, apelează `scan_port`, afișează și colectează rezultatele

---

## 2. Test local — scanare pe `127.0.0.1` din interiorul unui container

```bash
podman exec -it h1 python3 /apps/port_scanner.py 127.0.0.1 1 200
```

Majoritatea porturilor vor fi `CLOSED` sau `FILTERED` (containerul nu rulează servicii
pe loopback). Rezultatele se salvează în `/logs/scan_results.txt`.

---

## 3. Test între containere — h1 scanează h2

Porniți un server TCP pe h2:

```bash
podman exec -d h2 python3 /apps/tcp_server.py 5000
```

Rulați scanner-ul de pe h1:

```bash
podman exec -it h1 python3 /apps/port_scanner.py 10.0.10.2 4900 5100
```

> ✅ Așteptat: portul 5000 apare `OPEN`, restul `CLOSED` sau `FILTERED`.

Opriți serverul:

```bash
podman exec h2 pkill -f tcp_server.py
```

---

## 4. Analizați `logs/scan_results.txt`

```bash
cat ./logs/scan_results.txt | grep OPEN
```

- Câte porturi sunt `OPEN`?
- Corespund cu serviciile pornite?
- Vedeți porturi `FILTERED`? De ce?

---

## 5. Extensie opțională: rezumat și `--fast`

Adăugați la sfârșitul `scan_range` un rezumat:

```python
open_count     = results.count(r for r in results if "OPEN" in r)
closed_count   = ...
filtered_count = ...
print(f"\nRezumat: {open_count} OPEN, {closed_count} CLOSED, {filtered_count} FILTERED")
```

---

## 6. Întrebări de reflecție (în `logs/scan_results.txt`)

1. Care este diferența dintre un TCP connect scan și un SYN scan?
2. De ce un scan UDP este mai greu de interpretat decât un scan TCP?
3. De ce un firewall poate face porturile să apară `FILTERED` în loc de `CLOSED`?

---

## Deliverabil

- `apps/port_scanner.py` completat
- `logs/scan_results.txt` cu minimum 50 de porturi scanate + răspunsuri
