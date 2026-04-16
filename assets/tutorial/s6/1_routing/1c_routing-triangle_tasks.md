# Sarcini: Rutare statică în topologia triunghiului

---

## 1. Verificarea adreselor IP

Rulați în CLI Mininet:

```
r1 ip a
r2 ip a
r3 ip a
h1 ip a
h3 ip a
```

Confirmați că toate interfețele au adresele din schema de adresare.

---

## 2. Verificarea conectivității inițiale

Calea **h1 → r1 → r3 → h3** este pre-configurată. Testați:

```
h1 ping -c 4 10.0.3.2
h1 traceroute 10.0.3.2
```

> ✅ Așteptat: `h1 → 10.0.1.1 (r1) → 10.0.13.2 (r3) → 10.0.3.2 (h3)`
>
> r2 nu apare în traseu — este izolat.

---

## 3. Inspecția tabelelor de rutare

```
r1 ip route
r2 ip route
r3 ip route
```

Observați că:
- r1 trimite traficul spre `10.0.3.0/30` via `10.0.13.2` (r3, direct)
- r3 trimite traficul spre `10.0.1.0/30` via `10.0.13.1` (r1, direct)
- r2 **nu are rute** spre `10.0.1.0/30` sau `10.0.3.0/30` — este izolat intenționat

---

## 4. Conectarea lui r2 ca rută alternativă

Adăugați rutele necesare pentru ca r2 să poată participa la rutare:

**Pe r2:**
```
r2 ip route add 10.0.1.0/30 via 10.0.12.1
r2 ip route add 10.0.3.0/30 via 10.0.23.2
```

**Pe r1** — rută alternativă spre h3 prin r2:
```
r1 ip route add 10.0.3.0/30 via 10.0.12.2
```

> ⚠️ Această comandă va eșua cu `File exists` — r1 are deja o rută spre `10.0.3.0/30` via r3.
> Kernelul Linux nu permite două rute spre același prefix fără metrică diferită.
> Adăugați ruta cu o metrică mai mare (mai puțin preferată):

```
r1 ip route add 10.0.3.0/30 via 10.0.12.2 metric 20
```

**Pe r3** — rută alternativă spre h1 prin r2:
```
r3 ip route add 10.0.1.0/30 via 10.0.23.1 metric 20
```

---

## 5. Testați conectivitatea după adăugarea lui r2

```
h1 ping -c 4 10.0.3.2
h1 traceroute 10.0.3.2
```

> ✅ Ping-ul funcționează. Traceroute arată **în continuare calea directă** r1→r3 — ruta via r3 are metrica implicită (0) și este preferată față de cea via r2 (metric 20).

---

## 6. Exercițiu principal: Eliminarea rutei directe r1→r3

### Pasul 1 — Ștergeți ruta r1→r3 de pe r1

```
r1 ip route del 10.0.3.0/30 via 10.0.13.2
```

### Pasul 2 — Testați

```
h1 ping -c 4 10.0.3.2
h1 traceroute 10.0.3.2
```

> ✅ Ping-ul funcționează în continuare. Traceroute arată acum calea prin r2:
> `h1 → 10.0.1.1 (r1) → 10.0.12.2 (r2) → 10.0.23.2 (r3) → 10.0.3.2 (h3)`
>
> Kernelul a ales automat următoarea rută disponibilă.

### Pasul 3 — Confirmați că r2 vede trafic

```
r2 tcpdump -i r2-eth0 -n icmp > /tmp/s1.txt 2>&1 &
```

Rulați ping-ul din nou și confirmați că pachetele trec acum prin r2.

---

## 7. *Opțional*: Restaurarea rutei directe

```
r1 ip route add 10.0.3.0/30 via 10.0.13.2
h1 traceroute 10.0.3.2
```

> Traficul revine pe calea directă r1→r3 — ruta fără metrică explicită (metric 0) este din nou preferată.

---

## Deliverable

Creați fișierul `triangle_routing_output.txt` care să conțină:

- Output `ip route` de pe fiecare router după fiecare etapă (inițial, după task 4, după task 6)
- Output `ping` și `traceroute` pentru ambele căi (directă și prin r2)
- Un fragment de captură `tcpdump` de pe r2 care arată traficul după eliminarea rutei directe
- Un paragraf de 6–8 propoziții în care explicați:
  - de ce traficul a mers inițial direct prin r3 și nu prin r2
  - ce rol joacă metrica în alegerea rutei
  - ce s-a întâmplat când ați șters ruta directă
  - ce principiu al rutării statice ilustrează acest exercițiu