### Sarcini pentru studenti - Load Balancer Custom

Creati fisierul:

```text
stage3_lb_custom_output.txt
```

### 1. Verificati structura proiectului

Rulati:

```bash
ls
ls web1 web2 web3
```

Fiecare director trebuie sa contina `index.html`.

Daca apare o eroare de permisiuni, reparati ownership-ul:

```bash
sudo chown -R $USER:$USER web1 web2 web3
```

### 2. Completati TODO-ul din `simple_lb.py`

Functia de completat este:

```python
def get_next_backend():
    ...
```

Trebuie sa implementeze round-robin peste lista:

```python
BACKENDS = [
    ("web1", 8000),
    ("web2", 8000),
    ("web3", 8000)
]
```

### 3. Porniti arhitectura

```bash
docker compose -f docker-compose.lb-custom.yml up --build
```

### 4. Testati cu curl

```bash
for i in 1 2 3 4 5 6; do
  curl -s http://localhost:8080
  echo
done
```

Copiati output-ul in fisier.

### 5. Copiati logurile LB-ului

In consola ar trebui sa apara mesaje de forma:

```text
[INFO] ('172.x.x.x', 12345) -> web1:8000
[INFO] ('172.x.x.x', 12346) -> web2:8000
[INFO] ('172.x.x.x', 12347) -> web3:8000
```

### 6. Test backend cazut

Opriti `web2`:

```bash
docker compose -f docker-compose.lb-custom.yml stop web2
```

Trimiteti inca 6 cereri.

Notati:

* care cereri reusesc
* care cereri esueaza
* de ce LB-ul custom continua sa aleaga `web2`

### 7. Mini-raport

Raspundeti in 3-5 fraze:

1. Ce face LB-ul custom similar cu Nginx?
2. Ce NU face LB-ul custom?
3. Care este primul lucru pe care l-ati imbunatati?
