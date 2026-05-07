### Sarcini - SSH port forwarding catre un serviciu HTTP in container

Scop:

- sa accesati un server HTTP din containerul `web`
- folosind un tunel SSH prin containerul `ssh-bastion`
- fara sa expuneti direct portul HTTP al containerului `web` pe host

Rezultate:

- fisier de log: `ssh_forward_log.txt`

---

## 1. Porniti infrastructura

Asigurati-va ca aveti:

- `docker-compose.yml`
- Dockerfile pentru `ssh-bastion`
- fisierul `index.html` pentru containerul `web`

Porniti containerele:

```bash
docker compose up --build
````

Serviciile importante sunt:

* `web`: server HTTP intern, pe portul `8000`
* `ssh-bastion`: server SSH accesibil de pe host pe portul `2222`

Containerul `web` nu trebuie accesat direct de pe host. El va fi accesat prin tunelul SSH.

---

## 2. Verificati conectivitatea interna

Intrati in containerul `ssh-bastion`:

```bash
docker compose exec ssh-bastion bash
```

Din interiorul containerului:

```bash
apt-get update && apt-get install -y curl
curl http://web:8000/
```

Ar trebui sa vedeti continutul paginii servite de containerul `web`, de exemplu:

```html
<h1>Salut din containerul web!</h1>
<p>Ai ajuns aici printr-un tunel SSH.</p>
```

Copiati output-ul in `ssh_forward_log.txt` sub sectiunea:

```text
--- TEST DIRECT DIN ssh-bastion ---
<output>
```

Iesiti din container:

```bash
exit
```

---

## 3. Porniti tunelul SSH de pe host - Linux/macOS

De pe host, rulati:

```bash
ssh -L 9000:web:8000 labuser@localhost -p 2222
```

Parola este:

```text
labpass
```

Lasati aceasta sesiune deschisa cat timp testati tunelul.

Explicatie:

```text
localhost:9000 de pe host
  -> tunel SSH catre ssh-bastion
  -> web:8000 din reteaua Docker
```

---

## 4. Porniti tunelul SSH de pe host - Windows

Pe Windows, folositi PowerShell sau Windows Terminal.

Verificati ca aveti client SSH:

```powershell
ssh -V
```

Porniti tunelul:

```powershell
ssh -L 9000:web:8000 labuser@localhost -p 2222
```

Parola este:

```text
labpass
```

Lasati aceasta fereastra deschisa cat timp testati tunelul.

Intr-o alta fereastra PowerShell, testati tunelul:

```powershell
curl.exe http://localhost:9000/
```

---

## 5. Testati accesul HTTP prin tunel

Intr-un alt terminal de pe host, rulati:

Linux/macOS:

```bash
curl -v http://localhost:9000/
```

Windows PowerShell:

```powershell
curl.exe -v http://localhost:9000/
```

Ar trebui sa vedeti acelasi continut ca la testul direct din `ssh-bastion`:

```html
<h1>Salut din containerul web!</h1>
<p>Ai ajuns aici printr-un tunel SSH.</p>
```

Copiati output-ul in `ssh_forward_log.txt` sub sectiunea:

```text
--- TEST PRIN TUNEL (curl localhost:9000) ---
<output>
```

---

## 6. Problema frecventa: host key schimbat

Daca ati mai rulat laboratorul inainte, containerul `ssh-bastion` poate avea o alta cheie SSH dupa rebuild.

Eroare posibila:

```text
Host key for [localhost]:2222 has changed
Host key verification failed
```

Pe Linux/macOS, stergeti cheia veche cu:

```bash
ssh-keygen -f "$HOME/.ssh/known_hosts" -R "[localhost]:2222"
```

Pe Windows PowerShell:

```powershell
ssh-keygen -f "$env:USERPROFILE\.ssh\known_hosts" -R "[localhost]:2222"
```

Apoi rulati din nou comanda SSH:

```bash
ssh -L 9000:web:8000 labuser@localhost -p 2222
```

Pentru un laborator Docker temporar, se poate folosi si varianta:

```bash
ssh \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  -L 9000:web:8000 \
  labuser@localhost \
  -p 2222
```

Aceasta varianta este comoda pentru containere recreate frecvent, dar nu este recomandata ca practica generala pentru servere reale.

---

## 7. Intrebari de reflexie

La finalul fisierului `ssh_forward_log.txt`, raspundeti in cateva propozitii:

1. Ce rol are containerul `ssh-bastion` in acest scenariu?
2. De ce putem folosi `web` ca `DEST_HOST` in comanda `ssh -L`?
3. Ce s-ar schimba daca `web` ar rula pe alta masina sau pe alt IP?
4. Ce avantaje are port forwarding-ul fata de expunerea directa a portului `8000` pe host?

---

## Ideea principala

Comanda:

```bash
ssh -L 9000:web:8000 labuser@localhost -p 2222
```

creeaza un port local pe host:

```text
localhost:9000
```

Traficul trimis catre acest port este transmis prin conexiunea SSH catre `ssh-bastion`, iar de acolo este trimis mai departe catre:

```text
web:8000
```

Astfel, accesam un serviciu intern fara sa expunem direct portul sau pe host.
