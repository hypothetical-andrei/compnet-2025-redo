### Stage 4 - Comparatie intre Nginx si Load Balancer-ul Custom

### 1. Ce face bine LB-ul custom

LB-ul custom demonstreaza mecanismele de baza:

* accepta conexiuni TCP
* citeste cereri HTTP
* alege un backend
* trimite cererea mai departe
* returneaza raspunsul catre client

Dupa implementarea round-robin, cererile sunt distribuite intre `web1`, `web2`, `web3`.

### 2. Ce lipseste fata de Nginx

Nginx este mult mai robust. Comparativ, LB-ul custom nu are:

* health checks reale
* retry automat in versiunea de baza
* timeouts configurabile complet
* suport complet HTTP/1.1 si HTTP/2
* TLS
* buffering performant
* logging matur
* configurabilitate avansata

### 3. Backend cazut

Daca `web2` este oprit, versiunea de baza a LB-ului custom va continua sa trimita periodic cereri catre `web2`. Acele cereri vor esua.

Aceasta este o diferenta majora fata de un reverse proxy matur, care poate detecta backend-uri nefunctionale si le poate evita temporar.

### 4. Concurrency

LB-ul custom creeaza cate un thread pentru fiecare client. Acest lucru este simplu de inteles, dar nu este ideal pentru incarcari mari.

In plus, variabila globala `backend_index` este accesata de mai multe thread-uri. O versiune mai corecta ar trebui sa foloseasca un lock.

### 5. Versiunea finala propusa

In directorul `solutions` exista o versiune imbunatatita:

```text
solutions/simple_lb_final_solution.py
```

Aceasta adauga:

* lock pentru round-robin
* timeout pentru backend-uri
* retry pe urmatorul backend
* raspuns `503 Service Unavailable` daca toate backend-urile sunt cazute

### 6. Concluzie

Scopul exercitiului este sa arate ca un reverse proxy pare simplu conceptual, dar devine rapid complex cand apar:

* conexiuni concurente
* backend-uri lente
* backend-uri cazute
* protocoale HTTP reale
* cerinte de productie
