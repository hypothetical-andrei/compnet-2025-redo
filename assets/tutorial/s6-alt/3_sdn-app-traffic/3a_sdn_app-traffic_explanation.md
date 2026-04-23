# Trafic de aplicație prin SDN: servere și clienți Python

În stage-urile anterioare am:

- construit o topologie SDN cu Podman (h1, h2, h3 ca namespace-uri interne în `sdn-topology`)
- folosit un controller Os-Ken care permite traficul între h1 și h2 și blochează traficul către h3
- testat comportamentul cu `ping`

În acest stage vom trece la **trafic de aplicație**:

- un server TCP Python rulat în namespace-ul h2
- un client TCP Python rulat în namespace-ul h1
- un server UDP Python rulat în namespace-ul h3
- un client UDP Python rulat în namespace-ul h1

Vom observa:

- conexiune TCP reușită între h1 și h2 (permisă de controller)
- conexiune TCP eșuată între h1 și h3 (blocată de controller)
- după modificarea controllerului:
  - trafic UDP permis între h1 și h3
  - trafic TCP spre h3 în continuare blocat

---

## Porturi și adrese

| Rol              | Host | Adresă IP     | Port |
|------------------|------|---------------|------|
| server TCP       | h2   | 10.0.10.2/24  | 5000 |
| client TCP       | h1   | 10.0.10.1/24  | —    |
| server UDP       | h3   | 10.0.10.3/24  | 6000 |
| client UDP       | h1   | 10.0.10.1/24  | —    |

---

## Helpere disponibile în containerul topology

Scripturile Python se află la `/apps/` în container. Trei helpere sunt disponibile:

`host <hX> <comanda>` — rulează o comandă în namespace-ul unui host (foreground):
```bash
podman exec -it sdn-topology host h1 python3 /apps/tcp_client.py 10.0.10.2 5000
```

`bg <hX> <nume> <comanda>` — pornește un server în background într-un namespace:
```bash
podman exec sdn-topology bg h2 tcp-server python3 /apps/tcp_server.py 5000
```

`bg-stop <hX> <nume>` — oprește un server pornit cu `bg`:
```bash
podman exec sdn-topology bg-stop h2 tcp-server
```

Log-urile serverelor de fundal sunt la `/var/log/bg-hX-<nume>.log` în container:
```bash
podman exec sdn-topology cat /var/log/bg-h2-tcp-server.log
```

---

## Obiective

Studentul trebuie să:

- pornească serverul TCP pe h2 și să testeze clientul TCP de pe h1 (merge)
- încerce conexiunea TCP de la h1 la h3 (nu merge)
- pornească serverul UDP pe h3
- modifice controllerul Os-Ken astfel încât UDP de la h1 la h3 să fie permis
- testeze clientul UDP și să confirme comportamentul diferit TCP vs UDP
- salveze output-ul comenzilor într-un fișier de tip log

Comenzile și pașii concreți sunt în `3b_sdn_app-traffic_tasks.md`.
