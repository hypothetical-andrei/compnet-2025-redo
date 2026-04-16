# Protocoale de rutare
## RIP, EIGRP (context), OSPF (si idei link-state)

---

### Obiective
La finalul cursului, studentul poate:
- Explica rolul ruterului si ce este "forwarding" vs "routing"
- Explica ce contine o tabela de rutare si cum se alege "next hop"
- Diferentia rute statice vs dinamice si cand sunt utile
- Intelege diferentele distance-vector vs link-state
- Explica pe scurt RIP (hop count, timere, probleme tipice)
- Explica pe scurt OSPF (LSDB, hello, DR/BDR, SPF/Dijkstra, arii)
- Rula exemple: Bellman-Ford, Dijkstra, Mininet cu rutare statica

---

### Ce rol are un ruter?
- Un ruter conecteaza doua sau mai multe retele
- Primeste pachete si decide pe ce interfata le trimite mai departe
- Poate face si functii secundare: filtrare, NAT, QoS, tunelare (context)

[FIG] assets/images/fig-router-role.png

---

### Routing vs forwarding
- Forwarding: decizia locala "ies pe interfata X catre next hop Y"
- Routing: cum invat/mentin informatia care alimenteaza forwarding-ul (rute statice sau protocoale)

---

### Procesul de rutare (concept)
- Ruterul mentine o tabela de rutare
- Pentru fiecare prefix cunoscut: next hop, interfata, metrica, sursa (static/dinamic)
- Rutele direct conectate apar automat

---

### Tipuri de rute
- Statice (manual):
  - control precis
  - simple, bune pentru stub networks
  - nu sunt scalabile
- Dinamice (prin protocoale):
  - scalabile
  - se adapteaza la defecte (in functie de protocol)

---

### Metrici de rutare
- hop count (simplu)
- latency, bandwidth, reliability, load, cost administrativ (in functie de protocol)
- pot exista rute multiple cu aceeasi metrica (ECMP)

---

### Ce se modifica pe traseu (L2 vs L3)
- IP sursa/destinatie raman aceleasi
- MAC sursa/destinatie se schimba la fiecare hop
- TTL/Hop Limit scade la fiecare hop

[FIG] assets/images/fig-l2-l3-changes.png

---

### Tabela de rutare
- exista si pe host-uri, nu doar pe rutere
- se tine in RAM
- contine:
  - direct connected
  - rute statice
  - rute dinamice
  - ruta implicita (default)

[FIG] assets/images/fig-routing-table.png

---

### Clasificarea retelelor din perspectiva ruterului
- conectate (direct connected)
- cunoscute (statice/dinamice)
- necunoscute (default sau drop)

---

### Rutare asimetrica
- fiecare ruter decide local
- nu exista garantie ca drumul dus este identic cu drumul intors

---

### IGP vs EGP
- IGP: in interiorul unui sistem autonom (RIP, OSPF, EIGRP, IS-IS)
- EGP: intre sisteme autonome (BGP) (doar mentiune aici)

---

### Distance-vector (idea)
- ruterul nu stie topologia completa
- stie "distanta" catre retele + next hop
- update-uri periodice (clasic) sau incrementale (depinde de protocol)
- algoritm asociat: Bellman-Ford (conceptual)

[FIG] assets/images/fig-distance-vector.png

[SCENARIO] c7-assets/scenario-bellman-ford/

---

### RIP (Routing Information Protocol)
- metrica: hop count
- hop count maxim: 15 (16 = infinit)
- ruleaza peste UDP 520
- RIPv1: fara masca (fara CIDR/VLSM)
- RIPv2: include masca, multicast 224.0.0.9, poate avea autentificare
- RIPng: pentru IPv6

---

### Problema RIP: routing loops si count-to-infinity
- in anumite defecte, rutele "cresc" pana la infinit
- mecanisme clasice:
  - split horizon
  - route poisoning
  - holddown
  - timeout/flush

[FIG] assets/images/fig-rip-loop.png

---

### Mecanisme de evitare a buclelor de rutare (1/4) — Split horizon
- Un ruter nu retrimite informatia despre o ruta inapoi pe interfata de pe care a invatat-o.
- Exemplu: daca R1 a invatat ca reteaua X e accesibila prin R2, nu ii va anunta lui R2 ca "si eu stiu de X" — R2 deja stie.
- Previne bucle simple intre doi vecini.

---

### Mecanisme de evitare a buclelor de rutare (2/4) — Route poisoning
- Varianta mai agresiva a split horizon: in loc sa nu trimita ruta, ruterul o trimite cu metrica infinita (hop count = 16 in RIP).
- Semnalizeaza explicit ca ruta este down, accelerand convergenta.
- Poison reverse = split horizon cu anunt explicit de invaliditate.

---

### Mecanisme de evitare a buclelor de rutare (3/4) — Holddown timer
- Dupa ce o ruta devine invalida, ruterul intra in "holddown": ignora orice update care anunta aceeasi ruta cu o metrica mai mare sau egala, pentru o perioada de timp (ex. 180s in RIP).
- Scopul: sa nu accepte informatii vechi sau eronate care circula inca in retea.
- Dezavantaj: incetineste convergenta in cazuri legitime de schimbare.

---

### Mecanisme de evitare a buclelor de rutare (4/4) — Timeout si flush
- Timeout: daca o ruta nu este confirmata prin update-uri periodice intr-un interval (ex. 180s), este marcata ca invalida (metrica = 16).
- Flush: dupa inca un interval (ex. 240s total), ruta este stearsa complet din tabela.
- Asigura ca informatia veche nu persista la infinit.

[FIG] assets/images/fig-rip-loop.png

---

### Timere RIP (concept)
- update timer (30s): cat de des trimite ruterul update-uri periodice
- invalid timer (180s): dupa cat timp fara update o ruta devine invalida
- holddown timer (180s): cat timp este ignorata o ruta invalida pentru re-invatare
- flush timer (240s): dupa cat timp este stearsa complet din tabela

---

### IGRP si EIGRP (context Cisco)

**IGRP (Interior Gateway Routing Protocol)**
- Protocol Cisco proprietar, aparut ca alternativa la RIP
- Metrica compusa: bandwidth, delay, reliability, load (nu doar hop count)
- Hop count maxim: 255 (mult mai mare decat RIP)
- Inca distance-vector, cu aceleasi probleme de convergenta
- Considerat desuet; inlocuit complet de EIGRP

---

**EIGRP (Enhanced Interior Gateway Routing Protocol)**
- Tot Cisco proprietar (partial deschis din 2013, RFC 7868)
- Hibrid: combina avantaje distance-vector si link-state
  - Nu mentine o LSDB completa ca OSPF
  - Dar converge mult mai rapid decat RIP/IGRP clasic
- Algoritm: DUAL (Diffusing Update Algorithm)
  - Fiecare ruter mentine un "feasible successor" — un next hop de backup pre-calculat
  - La caderea unei rute, comuta instant pe feasible successor fara re-calcul
- Metrica: bandwidth + delay (implicit); poate include reliability si load
- Trimite update-uri doar la schimbari (nu periodic), reducand traficul
- Suporta VLSM si CIDR; versiuni pentru IPv4 si IPv6
- In practica: folosit in retele Cisco medii/mari unde OSPF e considerat prea complex

---

### Link-state (idea)
- fiecare ruter construieste o baza de date cu topologia (LSDB)
- calculeaza local rutele optime (SPF)
- algoritm asociat: Dijkstra (conceptual)

[FIG] assets/images/fig-link-state.png

[SCENARIO] c7-assets/scenario-dijkstra/

---

### OSPF (Open Shortest Path First)
- link-state IGP
- foloseste mesaje de tip hello si LSAs (concept)
- foloseste multicast (in functie de tipul de retea)
- imparte reteaua in arii; exista backbone (Area 0)

[FIG] assets/images/fig-ospf-areas.png

---

### OSPF: functionare (pe scurt)
- hello: descoperire vecini si mentinere adjacency
- sincronizare LSDB intre vecini
- alegere DR/BDR pe segmente multi-access
- calcul rute: SPF (Dijkstra) pe baza LSDB

---

### Unde intra Mininet in curs
- folosim o topologie simpla cu 3 rutere
- punem adrese si rute statice
- inspectam tabelele de rutare si verificam conectivitatea

[SCENARIO] c7-assets/scenario-mininet-routing/

---

### Sisteme autonome (AS)
- Un sistem autonom (AS) este un grup de retele IP aflate sub un singur control administrativ (ISP, companie, universitate)
- Fiecare AS primeste un numar unic: ASN (Autonomous System Number), alocat de IANA/RIR
- Exemple: AS15169 = Google, AS5430 = RCS&RDS
- Rutarea *in interiorul* unui AS foloseste IGP (RIP, OSPF, EIGRP)
- Rutarea *intre* AS-uri foloseste EGP — in practica, exclusiv BGP

---

### BGP (Border Gateway Protocol)
- Singurul protocol EGP folosit pe Internet astazi (BGP-4, RFC 4271)
- Ruleaza peste TCP port 179 — conexiune stabila intre perechi (peers)
- Nu calculeaza "cel mai scurt drum" — alege drumul pe baza de politici
- Metrica principala: AS-PATH (lista de AS-uri traversate)
- Spre deosebire de OSPF/RIP, BGP este un protocol de tip path-vector

---

### BGP: tipuri de sesiuni
- **eBGP (external BGP)**: intre rutere din AS-uri diferite — de obicei vecini directi
- **iBGP (internal BGP)**: intre rutere din acelasi AS — distribuie rutele invatate din exterior
- Diferenta importanta: rutele iBGP nu sunt redistribuite mai departe automat (no split horizon implicita => necesita full mesh sau route reflectors)

---

### BGP: atribute si selectia rutei
BGP alege ruta optima pe baza unui sir de atribute, in ordine de prioritate:
- **Weight** (Cisco local, nu se propaga)
- **Local preference** (preferinta in interiorul AS-ului)
- **AS-PATH length** (mai putine AS-uri traversate = mai bun)
- **Origin** (IGP > EGP > incomplete)
- **MED** (Multi-Exit Discriminator — indicatie pentru AS-ul vecin)
- **eBGP > iBGP**
- **IGP metric** catre next-hop

---

### BGP: de ce politici, nu metrici?
- Pe Internet, decizia de rutare nu este doar tehnica — este si comerciala
- Un ISP poate prefera o ruta mai lunga daca trece printr-un partener platit
- Poate evita o ruta care trece printr-un concurent
- Politicile se implementeaza cu route-maps si prefix-lists pe sesiunile BGP
- Acesta este motivul pentru care BGP este separat de IGP-uri

---

### Recapitulare
- rutele statice sunt bune pentru stub si topologii simple
- RIP: simplu, hop count, limitari si probleme de convergenta
- OSPF: link-state, scalabil, SPF, arii
- BGP: alt context (inter-AS)