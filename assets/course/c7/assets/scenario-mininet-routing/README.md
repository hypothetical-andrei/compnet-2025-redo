### Scenariu: Mininet (triunghi de rutere) + defecte si rutare asimetrica

Acest scenariu simuleaza o retea cu trei rutere conectate in triunghi, fiecare avand cate un host in spatele sau. Scopul este sa ilustreze comportamentul rutarii statice in trei situatii: functionare normala, defect de link cu ocolire automata, si rutare asimetrica (ruta lipsa pe retur). Toate scenariile ruleaza in Mininet pe Linux, fara hardware fizic.

#### Topologie

```
        h1
        |
     10.1.0.0/24
        |
       [r1]
      /     \
10.12.0.0/24  10.13.0.0/24
    /             \
  [r2]---10.23.0.0/24---[r3]
   |                      |
10.2.0.0/24          10.3.0.0/24
   |                      |
   h2                     h3
```

#### Adresare

| Nod | Interfata | Adresa IP       |
|-----|-----------|-----------------|
| h1  | h1-eth0   | 10.1.0.2/24     |
| r1  | r1-eth0   | 10.1.0.1/24     |
| r1  | r1-eth1   | 10.12.0.1/24    |
| r1  | r1-eth2   | 10.13.0.1/24    |
| h2  | h2-eth0   | 10.2.0.2/24     |
| r2  | r2-eth0   | 10.2.0.1/24     |
| r2  | r2-eth1   | 10.12.0.2/24    |
| r2  | r2-eth2   | 10.23.0.2/24    |
| h3  | h3-eth0   | 10.3.0.2/24     |
| r3  | r3-eth0   | 10.3.0.1/24     |
| r3  | r3-eth1   | 10.13.0.3/24    |
| r3  | r3-eth2   | 10.23.0.3/24    |

#### Cerinte
- Linux
- Mininet instalat
- rulare ca root (sudo)

#### Topologie
- 3 rutere: r1, r2, r3 (triunghi complet: r1-r2, r2-r3, r1-r3)
- 3 LAN-uri:
  - h1 in spatele lui r1 (10.1.0.0/24)
  - h2 in spatele lui r2 (10.2.0.0/24)
  - h3 in spatele lui r3 (10.3.0.0/24)

Link-uri intre rutere:
- r1-r2: 10.12.0.0/24
- r1-r3: 10.13.0.0/24
- r2-r3: 10.23.0.0/24

---

#### Scenariul 0: rutare simetrica completa (cazul normal)
Rulare:
```
sudo python3 triangle-net.py default
```

Ce se intampla:
- fiecare ruter primeste rute statice catre toate celelalte LAN-uri
- toate rutele sunt simetrice: fiecare pereche de LAN-uri poate comunica in ambele directii
- traficul merge pe calea directa intre rutere (fara ocoliri)

Comenzi utile in Mininet CLI:
```
r1 ip route
r2 ip route
r3 ip route
h1 ping -c 2 10.2.0.2
h1 ping -c 2 10.3.0.2
h2 ping -c 2 10.3.0.2
```

Ce sa urmaresti:
- toate ping-urile reusesc
- tabelele de rutare ale fiecarui ruter contin exact 2 rute statice (catre celelalte 2 LAN-uri)
- RTT-ul este consistent (nu exista ocoliri)

---

#### Scenariul 1: link-down (merge prin ruta alternativa)
Rulare:
```
sudo python3 triangle-net.py link-down
```
sau:
```
sudo bash run-link-down.sh
```

Ce se intampla:
- setam rute statice astfel incat traficul intre LAN-uri sa poata ocoli un link
- apoi coboram link-ul r1-r2
- ping h1 -> h2 ar trebui sa mearga in continuare prin r3

Comenzi utile in Mininet CLI:
```
r1 ip route
r2 ip route
r3 ip route
r1 ip link
h1 ping -c 2 10.2.0.2
h1 traceroute -n 10.2.0.2
```

Ce sa urmaresti:
- `r1 ip link` arata r1-eth1 ca DOWN
- ping h1 -> h2 reuseste in continuare (prin r3)
- traceroute arata 3 hopuri (h1 -> r1 -> r3 -> r2 -> h2) in loc de 2

---

#### Scenariul 2: rutare asimetrica (ruta doar intr-un sens)
Rulare:
```
sudo python3 triangle-net.py asymmetric
```
sau:
```
sudo bash run-asymmetric.sh
```

Ce se intampla:
- r1 are ruta catre 10.2.0.0/24 via r2
- r2 NU are ruta de intoarcere catre 10.1.0.0/24
- h1 -> h2 poate ajunge (request), dar raspunsul se pierde (no route back)

Comenzi utile:
```
r1 ip route
r2 ip route
r2 ip route get 10.1.0.2
h1 ping -c 2 10.2.0.2
```

Ce sa urmaristi:
- `r2 ip route` nu contine nicio ruta spre 10.1.0.0/24
- `r2 ip route get 10.1.0.2` returneaza eroare (`RTNETLINK answers: Network is unreachable`)
- ping-ul h1 -> h2 nu primeste raspuns (100% packet loss), desi pachetul ajunge la h2

---

#### Observatie importanta
Comparand scenariul 0 cu scenariul 2, diferenta este o singura ruta lipsa pe r2. Acesta este motivul clasic pentru care o conexiune "merge intr-un sens": request-ul ajunge, dar reply-ul nu are ruta de intoarcere si este aruncat.