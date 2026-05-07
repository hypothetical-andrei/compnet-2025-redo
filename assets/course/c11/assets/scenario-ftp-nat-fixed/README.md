# Scenario FTP - NAT si firewall

## Obiectiv

Observam de ce FTP este dificil in retele cu NAT/firewall si de ce modul pasiv este preferat in practica.

Topologie:

```text
client -- net_client -- natfw -- net_server -- ftp
```

Containere:

- `ftp`: server FTP real, bazat pe `pyftpdlib`
- `natfw`: container cu forwarding si NAT intre cele doua retele
- `client`: client Python care testeaza FTP passive si active

## Rulare

```bash
docker compose up --build
```

Clientul ruleaza testele si apoi se opreste. Este normal.

## Debug in ordine

### 1. Verificam containerele

```bash
docker compose ps
```

`ftp` si `natfw` ar trebui sa ramana pornite. `client` se poate opri dupa terminarea testului.

### 2. Verificam logurile NAT/firewall

```bash
docker compose logs natfw
```

Ar trebui sa vezi:

```text
NAT/FW ready
```

### 3. Verificam logurile FTP

```bash
docker compose logs ftp
```

Ar trebui sa vezi ca serverul asculta pe portul `2121` si foloseste porturile pasive `30000-30009`.

### 4. Rulam clientul manual

```bash
docker compose run --rm client
```

Rezultat asteptat:

- `passive=True` functioneaza
- `passive=False` poate esua; acesta este comportamentul discutat in laborator

## De ce nu folosim direct numele `ftp` in client?

Docker rezolva numele serviciilor doar intre containere aflate pe aceeasi retea Docker.

In acest scenariu, `client` si `ftp` sunt intentionat separate:

```text
client este doar in net_client
ftp este doar in net_server
```

De aceea clientul nu poate rezolva direct numele Docker `ftp`.

Folosim aliasul `ftp-server`, definit in `extra_hosts`, ca nume didactic pentru IP-ul serverului FTP din reteaua server.

## Ideea principala

In passive mode, clientul initiaza conexiunea de control si conexiunea de date.

In active mode, serverul incearca sa initieze conexiunea de date inapoi catre client. In prezenta NAT/firewall, aceasta conexiune poate fi blocata sau imposibila.
