# Scenario DNS - TTL si caching

## Obiectiv

Observam cum un resolver DNS recursiv cache-uieste raspunsurile primite de la un server authoritative si cum TTL-ul controleaza durata cache-ului.

Scenariul are trei containere:

- `auth`: server DNS authoritative pentru zona `example.test`
- `resolver`: resolver recursiv Unbound
- `client`: script Python care interogheaza resolver-ul pentru `www.example.test`

## Rulare

Porneste scenariul:

```bash
docker compose up --build
````

Clientul ruleaza cateva interogari si apoi se opreste. Acest lucru este normal.

## Debug pas cu pas

### 1. Verificam containerele

```bash
docker compose ps
```

Ar trebui sa existe cel putin:

```text
auth
resolver
```

Containerul `client` poate fi oprit deja, deoarece executa scriptul si termina.

### 2. Verificam serverul authoritative

Intrebam direct serverul authoritative:

```bash
docker compose exec auth dig @127.0.0.1 www.example.test A
```


Raspuns asteptat:

```text
www.example.test.  5  IN  A  10.0.0.42
```

Daca acest pas nu merge, problema este in configuratia BIND sau in fisierul zonei.

### 3. Verificam resolver-ul recursiv

Intrebam resolver-ul:

```bash
docker compose exec resolver drill @127.0.0.1 www.example.test A
```

Daca `drill` nu este disponibil, verificam logurile:

```bash
docker compose logs resolver
```

Daca resolver-ul returneaza `NXDOMAIN`, probabil trateaza `.test` ca zona locala speciala.

In `unbound.conf` trebuie sa existe:

```conf
local-zone: "test." nodefault
```

Daca resolver-ul returneaza `SERVFAIL`, probabil incearca DNSSEC validation pe zona locala nesemnata.

In `unbound.conf` trebuie sa existe:

```conf
domain-insecure: "example.test."
```

### 4. Rulam clientul manual

```bash
docker compose run --rm client
```

Clientul ar trebui sa afiseze ceva de forma:

```text
A = ['10.0.0.42'] TTL = 5
A = ['10.0.0.42'] TTL = 3
A = ['10.0.0.42'] TTL = 1
```

TTL-ul scade deoarece raspunsul este servit din cache-ul resolver-ului.

## Experiment: modificarea zonei

1. Porneste scenariul.
2. Observa IP-ul initial pentru `www.example.test`.
3. Modifica IP-ul din fisierul zonei, de exemplu:

```zone
www IN A 10.0.0.99
```

4. Incrementeaza serialul din zona.
5. Reporneste serverul authoritative:

```bash
docker compose restart auth
```

6. Ruleaza clientul din nou:

```bash
docker compose run --rm client
```

Este posibil ca noul IP sa nu apara imediat, deoarece resolver-ul poate avea inca vechiul raspuns in cache.

## Ideea principala

DNS nu este instant.

Resolver-ele cache-uiesc raspunsurile, iar TTL-ul decide cat timp poate fi refolosit un raspuns vechi.
