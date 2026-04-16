# Sarcini: Rutare statică în topologia triunghiului (Podman)

Porniți topologia înainte de a începe:

```bash
podman compose up -d
```

Verificați că toate containerele sunt pornite și scripturile de inițializare au rulat:

```bash
podman ps
podman logs r1
podman logs r2
podman logs r3
```

---

## 1. Verificarea adreselor IP

```bash
podman exec -it r1 ip a
podman exec -it r2 ip a
podman exec -it r3 ip a
podman exec -it h1 ip a
podman exec -it h3 ip a
```

Confirmați că adresele corespund schemei:

| Container | Adresă așteptată       |
|-----------|------------------------|
| h1        | 10.0.1.2/30            |
| r1        | 10.0.1.1/30, 10.0.12.1/30, 10.0.13.1/30 |
| r2        | 10.0.12.2/30, 10.0.23.1/30              |
| r3        | 10.0.23.2/30, 10.0.13.2/30, 10.0.3.1/30 |
| h3        | 10.0.3.2/30            |

---

## 2. Verificarea conectivității inițiale

Calea **h1 → r1 → r3 → h3** este pre-configurată. Testați:

```bash
podman exec -it h1 ping -c 4 10.0.3.2
podman exec -it h1 traceroute 10.0.3.2
```

> ✅ Așteptat: `h1 → 10.0.1.1 (r1) → 10.0.13.2 (r3) → 10.0.3.2 (h3)`
>
> r2 nu apare în traseu — este izolat.

---

## 3. Inspecția tabelelor de rutare

```bash
podman exec -it r1 ip route
podman exec -it r2 ip route
podman exec -it r3 ip route
```

Observați că:
- r1 trimite traficul spre `10.0.3.0/30` via `10.0.13.2` (r3, direct)
- r3 trimite traficul spre `10.0.1.0/30` via `10.0.13.1` (r1, direct)
- r2 **nu are rute** spre `10.0.1.0/30` sau `10.0.3.0/30` — este izolat intenționat

---

## 4. Conectarea lui r2 ca rută alternativă

Adăugați rutele necesare pentru ca r2 să poată participa la rutare.

**Pe r2:**
```bash
podman exec -it r2 ip route add 10.0.1.0/30 via 10.0.12.1
podman exec -it r2 ip route add 10.0.3.0/30 via 10.0.23.2
```

**Pe r1** — rută alternativă spre h3 prin r2:
```bash
podman exec -it r1 ip route add 10.0.3.0/30 via 10.0.12.2 metric 20
```

> ⚠️ Fără `metric 20`, comanda va eșua cu `File exists` — r1 are deja o rută spre
> `10.0.3.0/30` via r3 cu metrica implicită 0. Kernelul Linux nu permite două rute
> spre același prefix fără metrică diferită.

**Pe r3** — rută alternativă spre h1 prin r2:
```bash
podman exec -it r3 ip route add 10.0.1.0/30 via 10.0.23.1 metric 20
```

---

## 5. Testarea conectivității după adăugarea lui r2

```bash
podman exec -it h1 ping -c 4 10.0.3.2
podman exec -it h1 traceroute 10.0.3.2
```

> ✅ Ping-ul funcționează. Traceroute arată **în continuare calea directă** r1→r3 —
> ruta via r3 are metrica 0 și este preferată față de cea via r2 (metric 20).

---

## 6. Exercițiu principal: Eliminarea rutei directe r1→r3

### Pasul 1 — Ștergeți ruta r1→r3 de pe r1

```bash
podman exec -it r1 ip route del 10.0.3.0/30 via 10.0.13.2
```

### Pasul 2 — Testați

```bash
podman exec -it h1 ping -c 4 10.0.3.2
podman exec -it h1 traceroute 10.0.3.2
```

> ✅ Ping-ul funcționează în continuare. Traceroute arată acum calea prin r2:
> `h1 → 10.0.1.1 (r1) → 10.0.12.2 (r2) → 10.0.23.2 (r3) → 10.0.3.2 (h3)`

### Pasul 3 — Confirmați că r2 vede trafic

Într-un terminal separat, porniți captura pe r2:

```bash
podman exec -it r2 tcpdump -i any -n icmp
```

Într-un alt terminal, generați trafic:

```bash
podman exec -it h1 ping -c 4 10.0.3.2
```

Observați pachetele ICMP care tranzitează r2. Opriți `tcpdump` cu `Ctrl-C`.

> **Notă:** Spre deosebire de Mininet unde interfețele aveau nume fixe (`r2-eth0`),
> în Podman folosiți `tcpdump -i any` sau identificați interfața cu `ip a` înainte.

---

## 7. *Opțional*: Restaurarea rutei directe

```bash
podman exec -it r1 ip route add 10.0.3.0/30 via 10.0.13.2
podman exec -it h1 traceroute 10.0.3.2
```

> Traficul revine pe calea directă r1→r3 — ruta fără metrică explicită (metric 0)
> este din nou preferată.

---

## 8. Curățare

```bash
podman compose down
```

---

## Deliverabil

Creați fișierul `triangle_routing_output.txt` care să conțină:

- Output `ip route` de pe fiecare router după fiecare etapă (inițial, după task 4, după task 6)
- Output `ping` și `traceroute` pentru ambele căi (directă și prin r2)
- Un fragment de captură `tcpdump` de pe r2 care arată traficul după eliminarea rutei directe
- Un paragraf de 6–8 propoziții în care explicați:
  - de ce traficul a mers inițial direct prin r3 și nu prin r2
  - ce rol joacă metrica în alegerea rutei
  - ce s-a întâmplat când ați șters ruta directă
  - ce principiu al rutării statice ilustrează acest exercițiu
  - ce diferență ați observat față de configurarea în Mininet
