### Nivelul rețea: mecanisme de alocare și suport
### NAT/PAT, ARP, DHCP/BOOTP, NDP, ICMP

---

### Obiective
La finalul cursului, studentul poate:
- Explica de ce IPv4 a dus la NAT/PAT și ce compromisuri introduce
- Distinge între NAT static, NAT dinamic și PAT (NAT overload)
- Înțelege la nivel conceptual cum funcționează tabela NAT
- Explica ARP și proxy ARP (IPv4) și echivalentul IPv6 prin NDP
- Explica pașii DHCP (DORA) și rolul DHCP Relay
- Explica rolul ICMP (ping/traceroute, mesaje de eroare)
- Înțelege rolul ICMPv6 în NDP

---

### Context: de ce e nevoie de aceste mecanisme?
- Adresare L3 (IPv4/IPv6) e globală/rutabilă
- În practică trebuie:
  - alocare automată (DHCP/NDP)
  - mapare IP<->MAC (ARP/NDP)
  - suport pentru diagnostic și control (ICMP)
  - compatibilitate cu lipsa adreselor IPv4 (NAT/PAT)

[FIG] assets/images/fig-l3-support-map.png

---

### Epuizarea adreselor IPv4
- Problema majoră a IPv4: spațiu mic de adrese
- Soluții în timp:
  - adrese private reutilizabile (RFC1918)
  - NAT/PAT
  - tranziție IPv6 (lentă, dar continuă)

---

### Adrese private reutilizabile (RFC1918)
- 10.0.0.0/8
- 172.16.0.0/12
- 192.168.0.0/16
Notă: nu sunt rutabile global; trebuie traduse/încapsulate pentru Internet.

---

### Translatarea adreselor (NAT)
- În mod normal, ruterul forwardează fără să schimbe IP-urile
- NAT: modifică adresa sursă și/sau destinație
- Necesită mapare bidirecțională pentru a primi răspuns

[FIG] assets/images/fig-nat-basic.png

---

### Tabela NAT (concept)
- Ruterul păstrează corespondențe intern <-> extern
- Statică (config) sau dinamică (pe trafic)
- Exemplu simplu:
  - 192.168.0.1 -> 166.14.133.3

---

### Tipuri de translatare
- NAT static (1:1)
- NAT dinamic (pool de adrese publice)
- PAT / NAT overload (mulți -> 1 public, diferențiere prin port)

---

### NAT static (1:1)
- Problemă: server intern privat trebuie accesibil din exterior
- Soluție: mapare fixă între IP privat și IP public

[FIG] assets/images/fig-nat-static.png

---

### NAT dinamic (pool)
- Problemă: multe stații, puține IP-uri publice
- Soluție: pool de IP-uri publice alocate temporar (lease pe mapare)

[FIG] assets/images/fig-nat-dynamic.png

---

### PAT (Port Address Translation)
- Problemă: multe stații, o singură adresă publică
- Soluție: mapare per-flux folosind porturi pe ruter

Exemplu tabelă:
- 192.168.0.1:80 -> 166.14.133.3:62101
- 192.168.0.2:80 -> 166.14.133.3:63105

[FIG] assets/images/fig-pat.png

[SCENARIO] assets/scenario-nat-linux/

---

### Dezavantaje NAT/PAT
- În PAT, conexiunile din Internet către interior sunt dificil de inițiat (fără port forwarding)
- Încălcarea ideii end-to-end
- Dependență de L4 (porturi) pentru o problemă de L3
- Probleme cu unele protocoale și cu UDP (mai ales fără keepalive)
- Îngreunează tuneluri / VPN / aplicații P2P

---

### ARP (IPv4) și de ce există
- În Ethernet trebuie MAC destinație pentru a trimite un cadru
- ARP: IP -> MAC în rețeaua locală
- ARP request: broadcast
- ARP reply: unicast

[FIG] assets/images/fig-arp.png

[SCENARIO] assets/scenario-arp-capture/

---

### Proxy ARP (concept)
- Dacă IP-ul căutat e în altă rețea
- Ruterul poate răspunde cu MAC-ul lui (în locul destinației reale)

[FIG] assets/images/fig-proxy-arp.png

---

### BOOTP (istoric)
- Configurare IP prin server
- Nu suportă alocare dinamică reală
- DHCP este extensia practică; DHCP poate suporta clienți BOOTP (în general)

---

### DHCP: rol
- Alocare automată IP + parametri:
  - mască
  - default gateway
  - DNS
  - lease time

[FIG] assets/images/fig-dhcp-dora.png

[SCENARIO] assets/scenario-dhcp-capture/

---

### DHCP DORA (pași)
- Discover: client broadcast (UDP)
- Offer: server oferă IP + parametri
- Request: client acceptă (broadcast ca să notifice și alte servere)
- Acknowledge: server confirmă lease

---

### DHCP Relay
- Discover e broadcast (nu trece prin rutare)
- Relay pe ruter: transformă cererea și o trimite către serverul DHCP din altă rețea

[FIG] assets/images/fig-dhcp-relay.png

---

### NDP (IPv6)
- În IPv6, multe roluri care în IPv4 sunt separate:
  - descoperire vecini (echivalent ARP)
  - descoperire router (gateway)
  - prefix discovery
  - DAD (duplicate address detection)
- Folosește ICMPv6

[FIG] assets/images/fig-ndp.png

[SCENARIO] assets/scenario-ndp-capture/

---

### Neighbor Solicitation / Advertisement
- NS: solicitare către multicast solicitat-node (în loc de broadcast ca ARP)
- NA: răspuns unicast direct către solicitant (sau anunț nesolicitat)

Pași:
1. Host A trimite NS → multicast: "Cine are adresa IPv6 X? Eu sunt A (MAC aa:bb…)"
2. Doar nodul cu adresa X procesează NS-ul
3. Nodul X trimite NA → unicast către A: "Eu am adresa X, MAC-ul meu e cc:dd…"
4. Host A actualizează cache-ul de vecini (IPv6 → MAC)

[FIG] assets/images/fig-ndp-ns-na.png

---

### NDP: descoperire router (RS/RA)
- RS (Router Solicitation): trimis de hostul nou pe all-routers multicast — opțional
- RA (Router Advertisement): trimis de router periodic și ca răspuns la RS

Pași:
1. Host nou trimite RS → all-routers multicast: "Există vreun router pe link?" (opțional)
2. Routerul aude RS (sau trimite RA periodic, nesolicitat)
3. Routerul trimite RA → all-nodes multicast: prefix, MTU, hop limit, flag M/O, lifetime
4. Hostul procesează RA: reține routerul ca default gateway + prefix pentru SLAAC

[FIG] assets/images/fig-ndp-rs-ra.png

---

### Autoconfigurare IPv6
- Stateless (SLAAC):
  - link-local + DAD
  - prefix din RA
  - adresa globală rezultă din prefix + interface ID (sau token random)
- Stateful:
  - DHCPv6 pentru parametri suplimentari (DNS etc), uneori și pentru adresă

Pași SLAAC + DAD:
1. Host generează adresă link-local tentativă: fe80::/10 + interface ID (EUI-64 sau random)
2. DAD: trimite NS pentru propria adresă tentativă → dacă cineva răspunde = conflict
3. Fără conflict → link-local confirmată și activată
4. Host primește RA cu prefix global (ex: 2001:db8:1::/64) → construiește adresă globală
5. DAD repetat pentru adresa globală
6. Adresă globală activă — host complet configurat fără server DHCP

[FIG] assets/images/fig-ndp-slaac-dad.png

---

### ICMP: de ce există
- Rețelele produc erori și au nevoie de feedback
- ICMP:
  - mesaje de control și eroare
  - ping / traceroute (instrumente construite peste ICMP)
- Nu se trimit mesaje ICMP pentru erori de ICMP

[FIG] assets/images/fig-icmp-role.png

[SCENARIO] assets/scenario-icmp-traceroute/

---

### ICMPv6
- rol similar ICMP
- utilizat intens de NDP (de aceea filtrarea ICMPv6 "la grămadă" împiedică funcționarea IPv6)

---

### Recapitulare
- NAT/PAT: soluție practică pentru IPv4, cu compromisuri
- ARP: IP->MAC (IPv4)
- DHCP: configurare automată (IPv4)
- NDP: ARP + router/prefix discovery (IPv6)
- ICMP/ICMPv6: diagnostic + control

---

### Pregătire pentru Curs 7
- Rutare: RIP, OSPF (și ce înseamnă "tabele de rutare" în practică)