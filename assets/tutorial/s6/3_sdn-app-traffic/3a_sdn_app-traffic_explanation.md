# Trafic de aplicație prin SDN: servere și clienți Python

În stage-urile anterioare am:

- construit o topologie SDN simplă (h1, h2, h3 conectate la s1)
- folosit un controller Os-Ken care permite traficul între h1 și h2 și blochează traficul către h3
- testat comportamentul cu `ping`

În acest stage vom trece la **trafic de aplicație**:

- un server TCP Python rulat pe h2
- un client TCP Python rulat pe h1
- un server UDP Python rulat pe h3
- un client UDP Python rulat pe h1

Vom observa:

- conexiune TCP reușită între h1 și h2 (permisă de controller)
- conexiune TCP eșuată între h1 și h3 (blocată de controller)
- după modificarea controllerului:
  - trafic UDP permis între h1 și h3
  - trafic TCP spre h3 în continuare blocat

---

## Porturi și adrese

Pentru claritate vom folosi:

- server TCP pe h2: port 5000
- client TCP pe h1: conectează la `10.0.10.2:5000`
- server UDP pe h3: port 6000
- client UDP pe h1: trimite către `10.0.10.3:6000`

Topologia este aceeași ca în stage 2 — toate hosturile conectate la același switch:

```
      h1
      |
h2 - s1 - h3
```

Adrese IP:

| Host | Adresă IP     |
|------|---------------|
| h1   | 10.0.10.1/24  |
| h2   | 10.0.10.2/24  |
| h3   | 10.0.10.3/24  |

---

## Obiective

Studentul trebuie să:

- pornească serverul TCP pe h2 și să testeze clientul TCP de pe h1 (merge)
- încerce conexiune TCP de la h1 la h3 (nu merge)
- pornească serverul UDP pe h3
- modifice controllerul Os-Ken astfel încât UDP de la h1 la h3 să fie permis
- testeze clientul UDP și să confirme comportamentul diferit TCP vs UDP
- salveze output-ul comenzilor într-un fișier de tip log

Comenzile și pașii concreți sunt în `index_sdn_app-traffic_tasks.md`.