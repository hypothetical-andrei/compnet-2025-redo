# Trafic de aplicație prin SDN: servere și clienți Python în Podman

În stage-urile anterioare am:

- construit topologia SDN cu Podman Compose (h1, h2, h3 conectate la OVS `br0`)
- pornit un controller Os-Ken care permite traficul între h1 și h2 și blochează traficul către h3
- testat comportamentul cu `ping`

În acest stage vom trece la **trafic de aplicație**:

- un server TCP Python rulat pe h2
- un client TCP Python rulat pe h1
- un server UDP Python rulat pe h3
- un client UDP Python rulat pe h1

Vom observa:

- conexiune TCP reușită între h1 și h2 (permisă de controller)
- conexiune TCP eșuată între h1 și h3 (blocată de controller)
- după actualizarea controllerului:
  - trafic UDP permis între h1 și h3
  - trafic TCP spre h3 în continuare blocat

---

## Topologia (neschimbată față de Stage 2)

```
h1 ---- s1 (OVS br0) ---- h2
               |
              h3

[controller Os-Ken] <--TCP 6633--> [s1 OVS]
```

| Host | Interfață date | Adresă IP    |
|------|---------------|--------------|
| h1   | eth1          | 10.0.10.1/24 |
| h2   | eth1          | 10.0.10.2/24 |
| h3   | eth1          | 10.0.10.3/24 |

---

## Ce se schimbă față de Stage 2

### 1. Scripturile Python sunt montate în containere

Fișierele `tcp_server.py`, `tcp_client.py`, `udp_server.py`, `udp_client.py` sunt montate
ca volum read-only în directorul `/apps` al containerelor h1, h2, h3. Nu este necesară
reconstruirea imaginilor.

### 2. Controllerul primește logica actualizată (NEW)

Fișierul `sdn_controller.py` din directorul `controller/` este înlocuit cu versiunea care
diferențiază TCP de UDP pentru destinația h3:

- **TCP → h3**: blocat (drop), prioritate 20
- **UDP → h3**: permis (output port 3), prioritate 20
- **h1 ↔ h2**: permis în continuare, prioritate 10

Deoarece fișierul este montat ca volum în containerul `controller`, actualizarea lui
nu necesită `podman build` — este suficient `podman restart controller`.

### 3. Comenzile de interacțiune

În loc de CLI-ul Mininet (`h2 python3 tcp_server.py 5000 &`), folosim:

```bash
# Pornire server în background
podman exec -d h2 python3 /apps/tcp_server.py 5000

# Rulare client interactiv
podman exec -it h1 python3 /apps/tcp_client.py 10.0.10.2 5000
```

### 4. Ștergerea flow-urilor vechi

În Mininet, comanda era `sudo ovs-ofctl del-flows s1`. În Podman:

```bash
podman exec -it s1 ovs-ofctl del-flows br0 -O OpenFlow13
```

---

## Porturi folosite

| Serviciu     | Host | Port |
|--------------|------|------|
| Server TCP   | h2   | 5000 |
| Server UDP   | h3   | 6000 |

---

## Cum se pornește (dacă nu rulează deja din Stage 2)

```bash
# Din directorul stage 2 (unde se află compose.yaml)
podman compose up -d
podman logs -f s1        # așteptați "s1 este gata"
podman logs -f controller # așteptați "Table-miss flow instalat"
```

Completați toate sarcinile din fișierul `3b_podman-sdn-app_tasks.md`.
