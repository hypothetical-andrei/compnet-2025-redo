### Scenariu: MAC, ARP si observatie trafic Ethernet (simplu)

#### Obiectiv
- Identifici adresa MAC a interfetei tale
- Observi ARP (nivel 2/2.5) si cum apare in captura
- Conectezi conceptele: MAC dst/src, broadcast, learning de switch (conceptual)

#### Pasul 1: afla MAC-ul local
Linux:
- ip link

macOS:
- ifconfig

Windows:
- ipconfig /all

#### Pasul 2: curata cache ARP (optional)
Linux:
- sudo ip neigh flush all

macOS:
- sudo arp -ad

Windows (PowerShell Admin):
- arp -d *

#### Pasul 3: genereaza ARP
- ping gateway-ul local (ex: 192.168.1.1)

#### Pasul 4: captura
Linux/macOS:
- sudo tcpdump -i any -n arp

Wireshark:
- display filter: arp

Observa:
- ARP request e broadcast
- ARP reply e unicast