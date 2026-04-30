# Setup: Seminar 7 — Interceptare pachete, port scanner, IDS (Podman)

---

## Arhitectura

Două containere conectate la un bridge Podman cu adrese fixe:

```
h1 (10.0.10.1) ──── bridge sem7-net ──── h2 (10.0.10.2)
```

Ambele containere au `CAP_NET_RAW` pentru socket-uri AF_PACKET (necesare pentru
sniffer, filtru și IDS). Directorul proiectului este montat la `/sem7` în ambele
containere — editați scripturile pe host și rulați-le imediat fără rebuild.

---

## Structura fișierelor

```
sem7/
├── 0_setup.md
├── Dockerfile
├── docker-compose.yml
├── scripts/teardown.sh
├── logs/                        ← output-uri (scan_results.txt, ids_alerts.log etc.)
├── 1_sniffing/
│   ├── 1a_packet-sniffing_explanation.md
│   ├── 1b_packet_sniffer.py
│   └── 1c_packet-sniffing_tasks.md
├── 2_packet-filter/
│   ├── 2a_packet-filter.py
│   └── 2b_packet-filter_tasks.md
├── 3_port-scanning/
│   ├── 3a_port_scanner.py
│   └── 3b_port-scanner_tasks.md
├── 4_scan-detector/
│   ├── 4a_detect-scan.py
│   └── 4b_detect-scan_tasks.md
└── 5_mini-ids/
    ├── 5a_mini-ids.py
    ├── 5b_mini-ids_tasks.md
    └── udp_spray.py
```

---

## Cerințe

```bash
# Fedora / RHEL / Rocky
sudo dnf install -y podman podman-compose

# Ubuntu / Debian
sudo apt-get install -y podman podman-compose
```

---

## Pasul 1: curățarea sesiunilor anterioare

```bash
bash scripts/teardown.sh
```

---

## Pasul 2: construirea imaginilor

```bash
podman-compose build
```

---

## Pasul 3: pornirea lab-ului

```bash
podman-compose up -d
```

Verificați că ambele containere rulează:

```bash
podman ps --format "table {{.Names}}\t{{.Status}}"
```

---

## Pasul 4: verificarea conectivității

```bash
podman exec h1 ping -c 3 10.0.10.2
```

Interfața de date în fiecare container este `eth0`.

---

## Oprirea lab-ului

```bash
bash scripts/teardown.sh
```

---

## Corespondență Mininet → Podman

| Mininet | Podman |
|---------|--------|
| `h2 sudo python3 1b_packet_sniffer.py eth0` | `podman exec -it h2 python3 /sem7/1_sniffing/1b_packet_sniffer.py eth0` |
| `h1 python3 3a_port_scanner.py 10.0.10.2 1 200` | `podman exec -it h1 python3 /sem7/3_port-scanning/3a_port_scanner.py 10.0.10.2 1 200` |
| `h2 python3 tcp_server.py 5000 &` | `podman exec -d h2 python3 /sem7/5_mini-ids/tcp_server.py 5000` |
| `h2 pkill -f packet_sniffer.py` | `podman exec h2 pkill -f packet_sniffer.py` |
