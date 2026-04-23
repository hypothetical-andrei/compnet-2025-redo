# Sarcini: Rutare statică în topologia triunghiului (Podman)

Porniți topologia înainte de a începe:

```bash
podman-compose -f 1b_podman-compose.yaml up -d
```

Verificați că toate containerele sunt pornite și scripturile de inițializare au rulat:

```bash
podman ps
podman logs r1
podman logs r2
podman logs r3
```

> ⚠️ **Așteptați mesajul `Configurare completă`** în logurile fiecărui router înainte
> de a continua. Containerele pornesc în paralel și init script-urile rulează asincron
> — dacă executați comenzi prea devreme, next-hop-urile pot fi încă nereachable.
> Dacă un container nu apare în `podman ps`, rulați `podman logs <nume>` pentru diagnostic.

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
| h1        | 10.0.1.2/29            |
| r1        | 10.0.1.1/29, 10.0.12.1/29, 10.0.13.1/29 |
| r2        | 10.0.12.2/29, 10.0.23.1/29              |
| r3        | 10.0.23.2/29, 10.0.13.2/29, 10.0.3.1/29 |
| h3        | 10.0.3.2/29            |

---

## 2. Verificarea conectivității inițiale

Calea **h1 → r1 → r3 → h3** este pre-configurată. Testați:

```bash
podman exec -it h1 ping -c 4 10.0.3.2
podman exec -it h1 traceroute 10.0.3.2
```

> ✅ Așteptat: ping reușit. Traceroute poate arăta doar 1-2 hopuri vizibili
> (r1 și h3) din cauza limitărilor Podman rootless — acest lucru este normal.
> Dovada că calea este corectă este ping-ul reușit și absența lui r2 din rute.

> **Notă `traceroute`:** Dacă primiți `socket(AF_INET,3,1): Operation not permitted`,
> folosiți modul UDP explicit: `traceroute -U 10.0.3.2`

---

## 3. Inspecția tabelelor de rutare

```bash
podman exec -it r1 ip route
podman exec -it r2 ip route
podman exec -it r3 ip route
```

Observați că:
- r1 trimite traficul spre `10.0.3.0/29` via `10.0.13.2` (r3, direct)
- r3 trimite traficul spre `10.0.1.0/29` via `10.0.13.1` (r1, direct)
- r2 **nu are rute** spre `10.0.1.0/29` sau `10.0.3.0/29` — este izolat intenționat

---

## 4. Conectarea lui r2 ca rută alternativă

Înainte de a adăuga rute, verificați că toate containerele sunt complet inițializate
și că interfețele sunt configurate corect:

```bash
podman exec -it r1 ip a
podman exec -it r2 ip a
podman exec -it r3 ip a
```

Apoi verificați că next-hop-urile sunt accesibile — dacă oricare dintre aceste ping-uri
eșuează, așteptați câteva secunde și reîncercați:

```bash
podman exec -it r1 ping -c 1 10.0.12.2   # r1 -> r2
podman exec -it r1 ping -c 1 10.0.13.2   # r1 -> r3
podman exec -it r3 ping -c 1 10.0.23.1   # r3 -> r2
```

> ⚠️ Dacă ping-ul eșuează cu `Destination Host Unreachable` sau timeout, init script-ul
> celuilalt container nu a terminat încă. Așteptați 5-10 secunde și reîncercați.
> Puteți urmări progresul cu `podman logs r2` sau `podman logs r3`.

Odată ce ping-urile funcționează, adăugați rutele:

**Pe r2:**
```bash
podman exec -it r2 ip route add 10.0.1.0/29 via 10.0.12.1
podman exec -it r2 ip route add 10.0.3.0/29 via 10.0.23.2
```

**Pe r1** — rută alternativă spre h3 prin r2:
```bash
podman exec -it r1 ip route add 10.0.3.0/29 via 10.0.12.2 metric 20
```

> ⚠️ Fără `metric 20`, comanda va eșua cu `File exists` — r1 are deja o rută spre
> `10.0.3.0/29` via r3 cu metrica implicită 0. Kernelul Linux nu permite două rute
> spre același prefix fără metrică diferită.

**Pe r3** — rută alternativă spre h1 prin r2:
```bash
podman exec -it r3 ip route add 10.0.1.0/29 via 10.0.23.1 metric 20
```

---

## 5. Testarea conectivității după adăugarea lui r2

```bash
podman exec -it h1 ping -c 4 10.0.3.2
podman exec -it h1 traceroute 10.0.3.2
```

> ✅ Ping-ul funcționează. Ruta via r3 (metric 0) este în continuare preferată față
> de cea via r2 (metric 20) — confirmați cu `podman exec -it r1 ip route` că există
> ambele rute. Traceroute poate să nu arate toate hopurile în Podman rootless.

---

## 6. Exercițiu principal: Eliminarea rutei directe r1→r3

### Pasul 1 — Ștergeți ruta r1→r3 de pe r1

```bash
podman exec -it r1 ip route del 10.0.3.0/29 via 10.0.13.2
```

### Pasul 2 — Testați

```bash
podman exec -it h1 ping -c 4 10.0.3.2
podman exec -it h1 traceroute 10.0.3.2
```

> ✅ Ping-ul funcționează în continuare. Traceroute arată acum calea prin r2:
> `h1 → 10.0.1.1 (r1) → 10.0.12.2 (r2) → 10.0.23.2 (r3) → 10.0.3.2 (h3)`

### Pasul 3 — Confirmați că traficul trece prin r2

> **Limitare Podman rootless:** În modul rootless, rețelele Podman folosesc un stack
> de rețea în userspace (slirp4netns/pasta). Din această cauză, tcpdump pe un router
> intermediar (r2) **nu vede pachetele forwarded** — vede doar traficul destinat
> containerului însuși. Aceasta este o limitare a mediului, nu o eroare de configurare.

În loc de tcpdump pe r2, confirmați că traficul trece prin r2 în două moduri:

**Metoda 1 — tcpdump pe destinație (h3):**

Terminal 1 — capturați pe h3:
```bash
podman exec -it h3 tcpdump -i eth0 -n icmp
```

Terminal 2 — generați trafic:
```bash
podman exec -it h1 ping -c 4 10.0.3.2
```

> ✅ Așteptat: h3 vede pachetele ICMP request și reply. Aceasta confirmă că traficul
> ajunge la destinație pe calea h1→r1→r2→r3→h3.

**Metoda 2 — verificare rute (dovadă directă):**

```bash
podman exec -it r1 ip route
```

> ✅ Așteptat: singura rută spre `10.0.3.0/29` este `via 10.0.12.2 metric 20` —
> ruta directă via r3 nu mai există, deci traficul este forțat prin r2.

> **Notă `traceroute`:** În Podman rootless, traceroute arată de obicei doar 2 hopuri
> (r1 și h3) chiar și când traficul trece prin r2 și r3. Routerele intermediare
> forwardează corect pachetele dar nu generează răspunsuri ICMP TTL-exceeded vizibile
> în stiva de rețea userspace. Dovada că rutarea prin r2 funcționează este:
> ping reușit + tcpdump pe h3 care arată pachetele + tabela de rute pe r1 fără ruta directă.

---

## 7. *Opțional*: Restaurarea rutei directe

```bash
podman exec -it r1 ip route add 10.0.3.0/29 via 10.0.13.2
podman exec -it h1 traceroute 10.0.3.2
```

> Traficul revine pe calea directă r1→r3 — ruta fără metrică explicită (metric 0)
> este din nou preferată.

---

## 8. Curățare

```bash
podman-compose -f 1b_podman-compose.yaml down
```

---

## Deliverabil

Creați fișierul `triangle_routing_output.txt` care să conțină:

- Output `ip route` de pe fiecare router după fiecare etapă (inițial, după task 4, după task 6)
- Output `ping` și `traceroute` pentru ambele căi (directă și prin r2)
- Output `podman exec -it r1 ip route` după eliminarea rutei directe (fără ruta via r3)
- Output `tcpdump` de pe h3 care confirmă că pachetele ajung la destinație
- Output `tcpdump` de pe h3 care arată pachetele ICMP primite după eliminarea rutei directe
- Un paragraf de 6–8 propoziții în care explicați:
  - de ce traficul a mers inițial direct prin r3 și nu prin r2
  - ce rol joacă metrica în alegerea rutei
  - ce s-a întâmplat când ați șters ruta directă
  - ce principiu al rutării statice ilustrează acest exercițiu
  - ce diferență ați observat față de configurarea în Mininet