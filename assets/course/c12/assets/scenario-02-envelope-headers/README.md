# Scenario 2 - Envelope vs Headers + Bcc + Received chain

## Obiective

* observarea diferentei dintre envelope SMTP si headers RFC822
* observarea comportamentului Bcc
* inspectarea lantului Received

## 1. Porniti stack-ul

```bash
docker compose up -d
docker exec -it dms setup email add alice@example.test alicepw
docker exec -it dms setup email add bob@example.test bobpw
docker exec -it dms setup email add carol@example.test carolpw
```

## 2. Trimiteti un mesaj simplu

```bash
python3 scripts/send_mail_smtp.py \
  --smtp-host localhost \
  --smtp-port 587 \
  --user alice@example.test \
  --password alicepw \
  --to bob@example.test \
  --subject "Headers demo" \
  --body "Testing SMTP headers"
```

## 3. Inspectati mesajul in WebMail

Deschideti:

```text
http://localhost:8080
```

Login:

```text
bob@example.test / bobpw
```

Cautati optiunea de vizualizare a sursei mesajului sau a antetelor complete.

Identificati:

* From
* To
* Subject
* Date
* Message-ID
* Received

## 4. Experiment Bcc

```bash
python3 scripts/send_bcc_smtp.py \
  --smtp-host localhost \
  --smtp-port 587 \
  --user alice@example.test \
  --password alicepw \
  --to bob@example.test \
  --bcc carol@example.test \
  --subject "Bcc demo" \
  --body "Bob and Carol receive this, but only Bob is visible."
```

Verificati in WebMail:

* bob primeste mesajul
* carol primeste mesajul
* header-ul Bcc nu apare in mesajul final

## 5. Intrebari

1. Care este diferenta dintre MAIL FROM si header-ul From?
2. De ce Bcc nu apare in mesajul final?
3. Cine adauga liniile Received?
4. Care header-e pot fi falsificate de client?
