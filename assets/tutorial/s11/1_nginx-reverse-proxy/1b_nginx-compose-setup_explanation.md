### Stage 2 - Configurarea unei Arhitecturi cu 3 Backend-uri si Nginx Reverse Proxy

### Obiective

In aceasta etapa construim un mediu functional folosind Docker Compose:

* trei servere backend simple
* un container Nginx configurat ca reverse proxy si load balancer
* testare cu `curl`
* observarea algoritmului round-robin

### 1. Structura arhitecturii

```text
client -> nginx -> web1:8000
                -> web2:8000
                -> web3:8000
```

Clientul acceseaza sistemul prin:

```text
http://localhost:8080
```

### 2. Structura proiectului

Directorul trebuie sa aiba forma:

```text
.
├── docker-compose.nginx.yml
├── nginx.conf
├── web1/
│   └── index.html
├── web2/
│   └── index.html
└── web3/
    └── index.html
```

Fiecare backend ruleaza:

```bash
python -m http.server 8000
```

Directorul montat in `/app` devine radacina serverului web.

Exemplu:

```yaml
volumes:
  - ./web1:/app:ro
```

Asadar:

* `web1` serveste continutul din `./web1`
* `web2` serveste continutul din `./web2`
* `web3` serveste continutul din `./web3`

Fisierele `index.html` trebuie sa fie diferite pentru ca load balancing-ul sa fie vizibil.

### 3. Configuratia Nginx

Pentru seminar folosim `worker_processes 1`.

```nginx
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    upstream backend_pool {
        server web1:8000;
        server web2:8000;
        server web3:8000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend_pool;

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### 4. De ce `worker_processes 1`?

In productie, Nginx ruleaza de obicei cu:

```nginx
worker_processes auto;
```

In seminar folosim:

```nginx
worker_processes 1;
```

Motivul este didactic: cu un singur worker, comportamentul round-robin este mai usor de observat. Cu mai multi workeri, fiecare worker poate avea propria stare de balancing, iar testele scurte pot parea ca trimit toate cererile catre acelasi backend.

### 5. Pornirea arhitecturii

```bash
docker compose -f docker-compose.nginx.yml up --build
```

Intr-un alt terminal:

```bash
for i in 1 2 3 4 5 6; do
  curl -s http://localhost:8080
  echo
done
```

Rezultat asteptat:

```html
<h1>Hello from web1</h1>
<h1>Hello from web2</h1>
<h1>Hello from web3</h1>
<h1>Hello from web1</h1>
```

### 6. Debugging rapid

Verificati containerele:

```bash
docker compose -f docker-compose.nginx.yml ps
```

Verificati configuratia activa Nginx:

```bash
docker compose -f docker-compose.nginx.yml exec nginx nginx -T
```

Verificati conectivitatea interna:

```bash
docker compose -f docker-compose.nginx.yml exec nginx wget -qO- http://web1:8000
docker compose -f docker-compose.nginx.yml exec nginx wget -qO- http://web2:8000
docker compose -f docker-compose.nginx.yml exec nginx wget -qO- http://web3:8000
```

### 7. Probleme comune

Daca vedeti directory listing in loc de `index.html`, directorul montat nu contine `index.html`.

Daca nu puteti scrie in `web1`, `web2`, `web3`, verificati permisiunile. Uneori containerele creeaza fisiere sau directoare cu owner `root`.

Corectare:

```bash
sudo chown -R $USER:$USER web1 web2 web3
```

Daca toate raspunsurile par sa vina de la `web1`, verificati ca:

* `index.html` este diferit in fiecare backend
* `worker_processes` este `1`
* ati recreat containerele

```bash
docker compose -f docker-compose.nginx.yml down --remove-orphans
docker compose -f docker-compose.nginx.yml up --build --force-recreate
```
