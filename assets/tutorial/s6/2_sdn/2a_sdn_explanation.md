# Introducere SDN și topologia cu switch OpenFlow

În această secțiune vom folosi o topologie Mininet bazată pe un switch OpenFlow (s1), controlat de un controller extern Os-Ken. Vom vedea cum controllerul poate decide ce trafic este permis și ce trafic este blocat, prin instalarea de flow-uri în switch.

---

## Concept de bază SDN

Software Defined Networking (SDN) separă:

- **control plane** – logica de decizie (controllerul)
- **data plane** – dispozitivele care doar aplică regulile (switch-uri, routere)

În SDN:

- controllerul vorbește cu switch-urile printr-un protocol de control (de ex. OpenFlow)
- switch-urile trimit către controller pachetele necunoscute (packet_in)
- controllerul răspunde cu instrucțiuni (packet_out, flow_mod) care instalează reguli de tip match–action

---

## Topologia SDN folosită

Topologia folosită în Mininet:

```
h1 ---- s1 ---- h2
         |
        h3
```

Toate cele trei hosturi sunt conectate la același switch s1. s1 este un Open vSwitch configurat să folosească OpenFlow, controlat de un controller Os-Ken extern.

Schema de adresare (toate în același subnet):

| Host | Interfață  | Adresă IPv4    |
|------|------------|----------------|
| h1   | h1-eth0    | 10.0.10.1/24   |
| h2   | h2-eth0    | 10.0.10.2/24   |
| h3   | h3-eth0    | 10.0.10.3/24   |

---

## Comportament dorit (logica SDN)

Controllerul impune următoarea politică **la nivel de software**, nu prin topologie fizică:

- traficul între h1 și h2 este **permis** (h1 ↔ h2)
- traficul de la orice host către h3 este **blocat** (drop)

> ⚠️ h3 este conectat fizic la același switch ca h1 și h2 — izolarea lui este realizată exclusiv prin flow-urile instalate de controller, nu prin separare fizică. Acesta este principiul fundamental al SDN: politica de rețea este definită în software.

Implementarea face:

- la primul pachet (packet_in) dintre h1 și h2: instalează flow-uri bidirecționale în s1
- la un pachet cu destinația h3: instalează un flow de tip drop (fără acțiuni)

---

## Ce veți face în acest stage

- veți porni controllerul Os-Ken cu aplicația noastră simplă
- veți porni topologia Mininet cu switch-ul s1
- veți testa conectivitatea:
  - `h1 ping h2` trebuie să meargă
  - `h1 ping h3` trebuie să fie blocat
- veți inspecta flow table-ul din s1 cu `ovs-ofctl dump-flows`