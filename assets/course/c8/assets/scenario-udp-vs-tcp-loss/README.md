# UDP vs TCP sub pierderi de pachete — demo Mininet

## Obiectiv pedagogic

Scenariul demonstrează concret diferența fundamentală dintre cele două protocoale
de transport atunci când rețeaua pierde pachete:

| Protocol | Comportament la pierderi |
|----------|--------------------------|
| **UDP**  | Pachetele pierdute dispar definitiv — receptorul vede „găuri" în secvență |
| **TCP**  | Stratul de transport retransmite automat — aplicația primește stream-ul complet |

Studenții pot observa că aplicația TCP nu face nimic special: fiabilitatea este
asigurată transparent de protocol, nu de codul aplicației.

## Cerințe

- Linux (Ubuntu 20.04+ recomandat)
- Mininet: `sudo apt install mininet`
- Open vSwitch: `sudo apt install openvswitch-switch` (de obicei inclus cu Mininet)
- Python 3.6+

Verificare rapidă:
```bash
sudo mn --version
python3 --version
```

## Topologie

```
h1 (10.0.0.1) ──[loss]── s1 ──[loss]── h2 (10.0.0.2)
```

Ambele link-uri (h1↔s1 și s1↔h2) au pierderi artificiale configurate prin
`TCLink`. La 20% pe fiecare segment, probabilitatea ca un pachet să traverseze
ambele link-uri este ~64%, deci ~36% pierderi end-to-end — suficient pentru un
demo vizibil.

## Structura fișierelor

```
.
├── run.sh            # script principal — pornește Mininet și rulează ambele teste
├── topo.py           # topologie reutilizabilă (poate fi importată sau rulată direct)
├── udp_sender.py     # trimite 200 mesaje UDP numerotate (h1)
├── udp_receiver.py   # recepționează și raportează mesajele lipsă (h2)
├── tcp_sender.py     # trimite 200 linii peste TCP (h1)
└── tcp_receiver.py   # numără liniile primite și raportează totalul (h2)
```

## Cum rulezi

### Testul complet (recomandat)

```bash
chmod +x run.sh
sudo ./run.sh
```

Pierderi implicite: **20%**. Poți suprascrie:

```bash
sudo ./run.sh 10    # 10% loss
sudo ./run.sh 5     # 5% loss
```

Scriptul:
1. pornește Mininet cu topologia și loss-ul ales
2. rulează UDP receiver pe h2, UDP sender pe h1 — afișează raportul
3. rulează TCP receiver pe h2, TCP sender pe h1 — afișează raportul
4. oprește Mininet

### Explorare interactivă (CLI Mininet)

```bash
sudo python3 topo.py
```

Deschide CLI-ul Mininet. Din el poți:
```
mininet> h2 python3 udp_receiver.py &
mininet> h1 python3 udp_sender.py
mininet> h2 python3 tcp_receiver.py &
mininet> h1 python3 tcp_sender.py
mininet> exit
```

## Output așteptat

```
[run] UDP test  (best-effort — losses expected)
[udp_receiver] received 134 messages, range 0..198
[udp_receiver] missing count: 65
[udp_receiver] first missing: [1, 2, 4, 6, 8, ...]

[run] TCP test  (reliable stream — no losses expected)
[tcp_receiver] received lines: 200/200  (OK - stream complete)
```

Numărul de mesaje UDP pierdute variază la fiecare rulare (aleatoriu). Linia TCP
va arăta întotdeauna **200/200** — dar testul poate dura mai mult decât UDP
deoarece retransmisiile TCP adaugă latență.

## Parametri configurabili

În `topo.py` (funcția `build`):

| Parametru | Implicit | Efect |
|-----------|----------|-------|
| `loss`    | 20       | % pierderi per link (întreg sau float) |
| `delay`   | `None`   | Latență artificială, ex: `"50ms"` |

Exemplu cu delay:
```python
net = build(loss=10, delay="30ms")
```

## De ce TCP durează mai mult la pierderi mari?

TCP folosește **retransmisie cu timeout exponențial** (RTO). La 20% pierderi
end-to-end, un segment poate fi retransmis de mai multe ori înainte să ajungă.
Cu `COUNT=200` și `sleep=0.005s` între mesaje, sender-ul termină în ~1s, dar
receiver-ul poate să mai aștepte 10–30s pentru ultimele segmente retransmise.
De aceea `run.sh` nu mai folosește un `sleep` fix, ci **polling** — verifică
periodic fișierul de output al receiver-ului până apare rezultatul.