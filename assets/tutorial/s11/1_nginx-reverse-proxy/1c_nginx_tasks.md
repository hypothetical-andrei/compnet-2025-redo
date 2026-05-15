### Sarcini pentru studenti - Nginx Reverse Proxy

Creati fisierul:

```text
stage2_nginx_output.txt
```

### 1. Verificati structura proiectului

Rulati:

```bash
ls
ls web1 web2 web3
```

Notati daca fiecare backend are un `index.html`.

### 2. Porniti arhitectura

```bash
docker compose -f docker-compose.nginx.yml up --build
```

### 3. Testati cu curl

Rulati:

```bash
for i in 1 2 3 4 5; do
  curl -s http://localhost:8080
  echo
done
```

Copiati output-ul in fisier.

### 4. Explicatie scurta

In 2-3 fraze, explicati ce face algoritmul round-robin.

### 5. Debugging

Rulati cel putin doua comenzi de debugging:

```bash
docker compose -f docker-compose.nginx.yml ps
docker compose -f docker-compose.nginx.yml exec nginx nginx -T
docker compose -f docker-compose.nginx.yml exec nginx wget -qO- http://web1:8000
```

Scrieti ce ati verificat.

### 6. Bonus

Opriti un backend:

```bash
docker compose -f docker-compose.nginx.yml stop web2
```

Trimiteti inca 5 cereri. Notati ce se intampla.
