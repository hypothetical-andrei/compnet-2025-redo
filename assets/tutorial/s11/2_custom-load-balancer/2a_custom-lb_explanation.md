### Stage 3 - Implementarea unui Load Balancer Custom in Python

### Obiective

In aceasta sectiune implementam un reverse proxy HTTP foarte simplu, scris in Python.

Vom folosi:

* socket-uri TCP
* un algoritm round-robin
* Docker Compose pentru cele trei backend-uri
* `curl` pentru testare

Scopul nu este sa recream Nginx, ci sa intelegem ce probleme rezolva un reverse proxy real.

### 1. Arhitectura

```text
client -> lb-custom -> web1:8000
                    -> web2:8000
                    -> web3:8000
```

Serviciile `web1`, `web2`, `web3` sunt hostnames interne in reteaua Docker Compose.

### 2. Structura proiectului

```text
.
├── Dockerfile.lb
├── docker-compose.lb-custom.yml
├── simple_lb.py
├── web1/
│   └── index.html
├── web2/
│   └── index.html
└── web3/
    └── index.html
```

Daca directoarele `web1`, `web2`, `web3` sunt goale, serverul Python va afisa directory listing. Pentru testul de load balancing, fiecare director trebuie sa contina un `index.html` diferit.

### 3. Pornirea arhitecturii

Opriti mai intai exemplul cu Nginx, daca ruleaza:

```bash
docker compose -f ../1_nginx-reverse-proxy/docker-compose.nginx.yml down --remove-orphans
```

Porniti exemplul custom:

```bash
docker compose -f docker-compose.lb-custom.yml up --build
```

Testati:

```bash
for i in 1 2 3 4 5 6; do
  curl -s http://localhost:8080
  echo
done
```

### 4. Ce trebuie observat

Versiunea initiala este intentionat limitata. Ea ar trebui sa poata distribui cereri intre backend-uri dupa completarea TODO-ului de round-robin, dar nu are inca:

* health checks
* retry automat
* tratare robusta a backend-urilor cazute
* suport complet pentru HTTP
* mecanisme performante de concurrency

Aceste lipsuri sunt scopul exercitiului.
