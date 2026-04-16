# Sarcini Podman: configurare adrese, rute și testare

Aceste exerciții se realizează după pornirea topologiei:

```bash
podman-compose -f 3b_podman-compose.yaml up -d
```

Pentru a accesa un container, folosiți:

```bash
podman exec -it <nume_container> bash
```

unde `<nume_container>` este `h1`, `r1` sau `h2`.

---

## 1. Verificarea interfețelor

Rulați în containere separate:

```bash
podman exec -it h1 ip a
podman exec -it h2 ip a
podman exec -it r1 ip a
```

Adresele așteptate pentru h1 și h2 sunt fixe (definite în compose):

| Container | Interfață | Adresă așteptată |
|-----------|-----------|------------------|
| h1 | eth0 | 10.0.1.10/24 |
| h2 | eth0 | 10.0.2.10/24 |

> **Atenție — r1:** Podman nu permite adrese IP statice pe containere conectate la
> mai multe rețele simultan. r1 primește adrese **automat** din fiecare subnet.
> Uitați-vă la output-ul `ip a` pe r1 și notați adresele reale pe `eth0` și `eth1`
> — acestea sunt gateway-urile pe care le veți folosi în pașii următori.
>
> De obicei Podman alocă prima adresă disponibilă din subnet, de exemplu
> `10.0.1.1/24` și `10.0.2.1/24`, dar verificați întotdeauna înainte de a continua.

---

## 2. Testarea conectivității locale (host → router)

Înlocuiți `<r1-ip-net-a>` și `<r1-ip-net-b>` cu adresele reale găsite la pasul 1:

```bash
podman exec -it h1 ping -c 3 <r1-ip-net-a>
podman exec -it h2 ping -c 3 <r1-ip-net-b>
```

Dacă nu funcționează, verificați că adresele IP sunt corect atribuite (pasul 1).

---

## 3. Verificarea rutării pe r1

```bash
podman exec -it r1 sysctl net.ipv4.ip_forward
```

Valoarea așteptată este `1` — activat la pornire prin `sysctls:` în `compose.yaml`.

> **Notă:** Nu încercați să modificați această valoare cu `sysctl -w` din interiorul
> containerului — `/proc/sys` este montat read-only după pornire, chiar și cu
> `NET_ADMIN`. Valoarea se poate seta **doar** la crearea containerului, prin
> `sysctls:` în compose.

---

## 4. Adăugarea rutelor implicite pe h1 și h2

Spre deosebire de Mininet, rutele implicite **nu sunt configurate automat** de compose.
Trebuie adăugate manual. Folosiți adresele reale ale r1 găsite la pasul 1:

Pe h1:

```bash
podman exec -it h1 ip route add default via <r1-ip-net-a>
```

Pe h2:

```bash
podman exec -it h2 ip route add default via <r1-ip-net-b>
```

Verificare:

```bash
podman exec -it h1 ip route show
podman exec -it h2 ip route show
```

---

## 5. Testarea conectivității end-to-end

```bash
podman exec -it h1 ping -c 4 10.0.2.10
```

Dacă funcționează, `r1` a rutat pachetele corect între cele două subneturi.

---

## 6. Testarea traseului cu traceroute

```bash
podman exec -it h1 traceroute 10.0.2.10
```

Ar trebui să observați trecerea prin r1 (adresa sa din `net_a`) înainte de a ajunge la h2.

---

## 7. Capturarea traficului cu tcpdump

Identificați mai întâi interfața corectă pe r1 (cea din `net_a`, spre h1):

```bash
podman exec -it r1 ip a
```

Porniți captura pe interfața respectivă (de obicei `eth0`):

```bash
podman exec -it r1 tcpdump -i eth0 -n
```

Într-un alt terminal, generați trafic:

```bash
podman exec -it h1 ping 10.0.2.10
```

Observați pachetele ICMP care trec prin `r1`. Opriți `tcpdump` cu `Ctrl-C`.

> **Notă:** Puteți captura și pe `eth1` (interfața spre h2) pentru a vedea traficul pe celălalt segment.

---

## 8. Optional: test IPv6

Dacă doriți să explorați și IPv6, adăugați manual adrese pe containere.
Înlocuiți `eth0`/`eth1` pe r1 cu interfețele reale identificate la pasul 1:

```bash
podman exec -it h1 ip -6 addr add 2001:db8:10:1::10/64 dev eth0
podman exec -it r1 ip -6 addr add 2001:db8:10:1::1/64 dev eth0
podman exec -it r1 ip -6 addr add 2001:db8:10:2::1/64 dev eth1
podman exec -it h2 ip -6 addr add 2001:db8:10:2::10/64 dev eth0
```

Adăugați rute implicite IPv6:

```bash
podman exec -it h1 ip -6 route add default via 2001:db8:10:1::1
podman exec -it h2 ip -6 route add default via 2001:db8:10:2::1
```

Testați:

```bash
podman exec -it h1 ping6 -c 3 2001:db8:10:2::10
```

---

## 9. Curățare

La finalul laboratorului, opriți și ștergeți containerele:

```bash
podman-compose -f 3b_podman-compose.yaml down
```

---

## Deliverabil

Creați fișierul:

```
podman_lab_output.txt
```

Acesta trebuie să conțină:
- comenzile folosite
- output-ul la `ip a`, `ping`, `traceroute` și `tcpdump` (captură parțială)
- o explicație de 5–7 propoziții în care descrieți:
  - cum au fost folosite subrețelele
  - rolul rutei implicite
  - de ce `r1` este necesar pentru comunicație
  - ce diferență ați observat față de configurarea în Mininet

Acest fișier va fi încărcat ca dovadă a finalizării laboratorului.