### Sarcini - Stage 4: LB Custom in Compose

Creati fisierul:

```text
stage4_lb_vs_nginx.txt
```

---

### 1. Output pentru 6 cereri

Executati:

```bash
for i in 1 2 3 4 5 6; do
  curl -s http://localhost:8080
  echo
done
```

Copiati raspunsurile obtinute.

Observati:

- daca backend-urile alterneaza
- daca algoritmul round-robin functioneaza corect

---

### 2. Logurile LB-ului

Afisati logurile:

```bash
docker compose -f docker-compose.lb-custom.yml logs lb-custom
```

Copiati logurile relevante.

Identificati:

- conexiunile clientilor
- backend-ul selectat
- eventuale erori

---

### 3. Test backend indisponibil

Opriti unul dintre backend-uri:

```bash
docker compose -f docker-compose.lb-custom.yml stop web2
```

Trimiteti din nou 6 cereri:

```bash
for i in 1 2 3 4 5 6; do
  curl -s http://localhost:8080
  echo
done
```

Observati:

- daca load balancer-ul continua sa functioneze
- daca apar erori
- ce se intampla cand backend-ul selectat nu raspunde

---

### 4. Implementare toleranta de baza la defecte

Extindeti implementarea astfel incat:

- daca un backend nu raspunde:
  - sa fie incercat urmatorul backend
- toate backend-urile sa fie incercate cel mult o singura data
- daca toate backend-urile sunt indisponibile:
  - sa fie trimis:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: text/plain

No backend available
```

---

### 5. Retestare dupa implementare

Cu `web2` oprit, repetati:

```bash
for i in 1 2 3 4 5 6; do
  curl -s http://localhost:8080
  echo
done
```

Verificati:

- daca cererile continua sa functioneze
- daca load balancer-ul evita backend-ul indisponibil
- daca raspunsurile vin doar de la backend-urile active

---

### 6. Comparatie Nginx vs LB custom

Scrieti maxim 6-8 fraze despre:

- doua lucruri pe care LB-ul custom le face bine
- doua lucruri pe care LB-ul custom le face prost
- un aspect la care NGINX este mult superior
- o idee de imbunatatire pentru LB-ul custom

---

### 7. Bonus

Opriti toate backend-urile:

```bash
docker compose -f docker-compose.lb-custom.yml stop web1 web2 web3
```

Trimiteti o cerere:

```bash
curl -v http://localhost:8080
```

Verificati:

- daca este returnat codul HTTP 503
- daca mesajul este:

```text
No backend available
```

Add this final section to the markdown:

````md
---

## Ce trebuie incarcat

Arhivati continutul proiectului intr-un fisier:

```text
stage4_lb_custom.zip
````

Arhiva trebuie sa contina:

```text
2_custom-load-balancer/
```

inclusiv:

* `simple_lb.py`
* `docker-compose.lb-custom.yml`
* eventuale modificari suplimentare realizate
* fisierul:

  * `stage4_lb_vs_nginx.txt`

---

## Cerinte minime

Pentru punctaj complet:

* load balancing round-robin functional
* tratarea backend-urilor indisponibile
* returnarea codului HTTP 503 daca toate backend-urile sunt indisponibile
* completarea fisierului de raspunsuri
* explicatiile comparative NGINX vs LB custom

---

## Observatii

Codul trebuie sa poata fi pornit folosind:

```bash
docker compose -f docker-compose.lb-custom.yml up --build
```

Nu includeti:

* directoare `.git`
* directoare `__pycache__`
* fisiere temporare
* imagini Docker exportate

