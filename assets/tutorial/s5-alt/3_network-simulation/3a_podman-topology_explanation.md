# Introducere în simularea de rețea cu Podman Compose

În această secțiune vom folosi **Podman Compose** pentru a crea o topologie de rețea echivalentă cu cea din laboratorul Mininet: două hosturi și un nod intermediar care se comportă ca un router. Scopul este să configurați manual adrese IP, rute și să verificați funcționarea rețelei folosind comenzi precum `ping`, `traceroute` și `tcpdump`.

---

## De ce Podman Compose

Podman Compose folosește containere Linux pentru a emula noduri de rețea, oferind un mediu mai aproape de infrastructura reală față de Mininet. Fiecare container:
- rulează o instanță independentă de Linux
- are propriile interfețe de rețea virtuale
- poate executa comenzi reale de rețea (`ip`, `ping`, `tcpdump`, `traceroute` etc.)

Avantajul față de Mininet:
- nu necesită un kernel modificat sau drepturi `sudo` la nivel de sistem
- topologia este descrisă declarativ într-un fișier `compose.yaml`
- containerele pot fi pornite, oprite și reinițializate ușor
- aproape de modul în care funcționează infrastructura reală bazată pe containere

---

## Topologia utilizată

```
h1 ----- r1 ----- h2
```

- **h1** și **h2** sunt hosturi finale, fiecare în câte un subnet diferit
- **r1** este routerul intermediar, conectat la ambele subneturi

---

## Rețelele Podman (echivalentul legăturilor Mininet)

În loc de link-uri punct-la-punct ca în Mininet, Podman Compose folosește **rețele bridge** definite explicit. Vom crea două rețele:

| Rețea Podman | Subnet | Echivalent Mininet |
|---|---|---|
| `net_a` | `10.0.1.0/24` | legătura h1 — r1 |
| `net_b` | `10.0.2.0/24` | legătura h2 — r1 |

---

## Schema de adresare

| Nod | Interfață (în container) | Adresă IPv4 |
|-----|--------------------------|-------------|
| h1  | eth0                     | 10.0.1.10/24 |
| r1  | eth0 (spre h1)           | 10.0.1.1/24  |
| h2  | eth0                     | 10.0.2.10/24 |
| r1  | eth1 (spre h2)           | 10.0.2.1/24  |

> **Notă:** Podman atribuie interfețele în ordinea în care containerul este conectat la rețele. Verificați întotdeauna cu `ip a` înainte de a configura rute.

---

## Imaginea de container folosită

Toate containerele folosesc imaginea **`nicolaka/netshoot`**, care include preinstalate toate utilitarele de rețea necesare: `ping`, `traceroute`, `tcpdump`, `ip`, `curl` etc.

---

## Diferențe față de Mininet

| Aspect | Mininet | Podman Compose |
|--------|---------|----------------|
| Izolare noduri | Namespace-uri de proces | Containere separate |
| Configurare IP | `setIP()` în Python | `ip addr add` în shell sau `ipv4_address` în compose |
| Forwarding IP | `sysctl` în script | `sysctl` în container + `privileged: true` |
| CLI interactiv | `mininet> h1 ping ...` | `podman exec -it h1 ping ...` sau `podman attach h1` |
| Capturare trafic | `tcpdump` în CLI Mininet | `tcpdump` direct în containerul `r1` |

---

## Cum se pornește topologia

```bash
# Pornire
podman-compose -f 3b_podman-compose.yaml up -d

# Accesarea unui container
podman exec -it h1 bash
podman exec -it r1 bash
podman exec -it h2 bash

# Oprire și ștergere
podman compose down
```

---

## Obiectivele studentului

- să pornească topologia cu `podman-compose up -d`
- să verifice configurațiile IP pe fiecare container
- să activeze forwardarea IP pe `r1`
- să configureze rute implicite pe `h1` și `h2`
- să verifice conectivitatea cu `ping`
- să observe traseul cu `traceroute`
- să captureze pachete cu `tcpdump`

Completați toate sarcinile din fișierul `3c_podman-config_tasks.md`.