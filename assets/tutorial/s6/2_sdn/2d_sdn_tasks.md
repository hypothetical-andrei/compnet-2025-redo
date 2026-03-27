# Sarcini: Topologia SDN cu Os-Ken și switch OpenFlow

---

## 1. Pornirea controllerului Os-Ken

Într-un terminal separat (NU în Mininet), rulați:

```bash
osken-manager index_sdn_os-ken_controller.py
```

Ar trebui să vedeți loguri Os-Ken și eventual un mesaj când se conectează switch-ul.

---

## 2. Pornirea topologiei Mininet SDN

În alt terminal:

```bash
sudo python3 index_sdn_topo_switch.py
```

După pornire, veți intra în CLI-ul Mininet (`mininet>`).

Verificați hosturile:

```
h1 ip a
h2 ip a
h3 ip a
```

---

## 3. Testarea conectivității cu ping

#### a) h1 către h2 (trebuie să meargă)

```
h1 ping -c 3 10.0.10.2
```

Ar trebui să vedeți reply-uri și să apară flow-uri noi în s1.

#### b) h1 către h3 (trebuie să fie blocat)

```
h1 ping -c 3 10.0.10.3
```

Ar trebui să vedeți timeout (no reply). Controllerul instalează un flow de tip drop.

---

## 4. Inspectarea flow table-ului

Comanda `ovs-ofctl` trebuie rulată **în afara CLI-ului Mininet**, într-un terminal separat de pe host:

```bash
sudo ovs-ofctl dump-flows s1
```

Alternativ, din CLI-ul Mininet folosind socket-ul Unix al switch-ului:

```
s1 ovs-ofctl dump-flows unix:/var/run/openvswitch/s1.mgmt
```

Analizați:

- există flow-ul table-miss (prioritate 0)?
- există flow-uri pentru traficul 10.0.10.1 ↔ 10.0.10.2?
- există flow-uri de tip drop pentru destinația 10.0.10.3?

---

## 5. *Opțional*: captură de trafic

```
s1 tcpdump -i s1-eth1 -n icmp > /tmp/s1.txt 2>&1 &
h1 ping -c 3 10.0.10.2
s1 pkill tcpdump
s1 cat /tmp/s1.txt
```

Observați pachetele ICMP. Notați că pentru traficul blocat spre h3, pachetele nu apar pe interfață după ce flow-ul de drop a fost instalat.

---

## Deliverable parțial

Creați fișierul `sdn_stage2_output.txt` care să conțină:

- output de la:
  - `h1 ping -c 3 10.0.10.2`
  - `h1 ping -c 3 10.0.10.3`
- output complet de la `ovs-ofctl dump-flows s1`
- 5–7 propoziții în care explicați:
  - cum se vede în flow table faptul că traficul h1 ↔ h2 este permis
  - cum se vede faptul că traficul către h3 este blocat
  - ce rol are regula table-miss
  - de ce h3 este izolat prin politică SDN și nu prin topologie fizică

Acest fișier va fi completat în Stage 3 cu teste pe servere/clienți Python.