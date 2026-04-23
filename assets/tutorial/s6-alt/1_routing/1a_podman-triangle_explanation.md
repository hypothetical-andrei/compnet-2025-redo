# Introducere: Rutare statică pe trei routere (topologie triunghi) cu Podman Compose

În această secțiune vom folosi **Podman Compose** pentru a crea o topologie cu trei routere Linux și două hosturi, echivalentă cu laboratorul Mininet. Scopul este să observăm cum rutarea statică determină calea traficului și cum modificarea rutelor redirecționează traficul în timp real.

---

## Topologia

```
h1
 |
r1 ----- r2
 \       /
  \     /
    r3
    |
    h3
```

- **h1** — host sursă, conectat la r1
- **h3** — host destinație, conectat la r3
- **r1, r2, r3** — routere Linux (containere cu IP forwarding activat)
- **3 linkuri router-router**: r1–r2, r2–r3, r1–r3

---

## Cum modelăm legăturile punct-la-punct în Podman

În Mininet, fiecare `addLink` creează o pereche veth dedicată între două noduri. În Podman Compose, legăturile punct-la-punct se modelează cu **rețele bridge cu câte două containere**:

| Rețea Podman   | Subnet         | Noduri conectate |
|----------------|----------------|------------------|
| `net_h1_r1`    | 10.0.1.0/29    | h1, r1           |
| `net_r1_r2`    | 10.0.12.0/29   | r1, r2           |
| `net_r2_r3`    | 10.0.23.0/29   | r2, r3           |
| `net_r1_r3`    | 10.0.13.0/29   | r1, r3           |
| `net_r3_h3`    | 10.0.3.0/29    | r3, h3           |

Fiecare rețea apare ca o interfață separată în containerele conectate la ea.

---

## Schema de adresare

| Legătură   | Subnet        | IP stânga          | IP dreapta         |
|------------|---------------|--------------------|--------------------|
| h1 ↔ r1    | 10.0.1.0/29   | h1: 10.0.1.2       | r1: 10.0.1.1       |
| r1 ↔ r2    | 10.0.12.0/29  | r1: 10.0.12.1      | r2: 10.0.12.2      |
| r2 ↔ r3    | 10.0.23.0/29  | r2: 10.0.23.1      | r3: 10.0.23.2      |
| r1 ↔ r3    | 10.0.13.0/29  | r1: 10.0.13.1      | r3: 10.0.13.2      |
| r3 ↔ h3    | 10.0.3.0/29   | r3: 10.0.3.1       | h3: 10.0.3.2       |

---

## Starea inițială la pornire

La pornire, sunt pre-configurate rutele pentru calea **h1 → r1 → r3 → h3**.
**r2 este izolat intenționat** — nu are rute spre h1 sau h3.

| Nod | Rută adăugată  | Via               |
|-----|----------------|-------------------|
| h1  | default        | 10.0.1.1 (r1)     |
| h3  | default        | 10.0.3.1 (r3)     |
| r1  | 10.0.3.0/29    | 10.0.13.2 (r3)    |
| r3  | 10.0.1.0/29    | 10.0.13.1 (r1)    |

Legătura r1–r2–r3 există fizic (rețelele sunt active), dar traficul nu o traversează.

---

## Cum funcționează scriptul de inițializare

Deoarece containerele multi-homed (r1, r2, r3) primesc interfețe în ordine nedeterministă, **adresele IP și rutele nu pot fi setate static în `compose.yaml`**. În schimb, fiecare container rulează un script shell (`init.sh`) care:

1. Identifică interfața corectă pe baza rețelei la care este conectată (via ARP/neighbor sau prefix de subnet)
2. Asignează adresele IP cu `ip addr add`
3. Adaugă rutele inițiale cu `ip route add`

Scripturile se află în directorul `scripts/` și sunt montate ca volume read-only în containere.

---

## Diferențe față de Mininet

| Aspect | Mininet | Podman Compose |
|--------|---------|----------------|
| Linkuri P2P | veth perechi izolate | bridge-uri cu două containere |
| Interfețe numite | `r1-eth0`, `r1-eth1` etc. | `eth0`, `eth1` ... (ordine nedeterministă) |
| Config IP inițială | `setIP()` în Python | script `init.sh` per container |
| Rute inițiale | `node.cmd("ip route add ...")` | același script `init.sh` |
| CLI interactiv | `mininet> r1 ip route del ...` | `podman exec -it r1 ip route del ...` |
| Modificare rute live | în CLI Mininet | `podman exec -it <nod> <comandă>` |

---

## Cum se pornește topologia

```bash
# Pornire
podman-compose -f 1b_podman-compose.yaml up -d

# Accesarea unui nod
podman exec -it r1 bash
podman exec -it h1 bash

# Oprire și curățare
podman-compose -f 1b_podman-compose.yaml down
```

---

## Obiectivele studentului

- să pornească topologia și să verifice adresele IP și rutele inițiale
- să confirme calea activă h1→r1→r3→h3 cu `ping` și `traceroute`
- să conecteze r2 ca rută alternativă prin adăugarea manuală de rute
- să observe efectul metricii asupra alegerii rutei
- să elimine ruta directă r1→r3 și să observe redirecționarea automată prin r2
- să captureze trafic ICMP pe r2 cu `tcpdump`

Completați toate sarcinile din fișierul `1c_podman-triangle_tasks.md`.
