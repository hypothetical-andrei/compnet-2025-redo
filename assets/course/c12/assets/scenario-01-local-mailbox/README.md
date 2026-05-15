# Scenario 1 - Local mailbox stack

## Obiective

* pornirea unui stack local de e-mail
* crearea unor casute postale
* trimiterea unui mesaj prin SMTP submission
* citirea mesajului prin IMAP si POP3
* accesarea WebMail prin Roundcube

## 1. Porniti stack-ul

```bash
docker compose up -d
```

## 2. Creati mailbox-uri

```bash
docker exec -it dms setup email add alice@example.test alicepw
docker exec -it dms setup email add bob@example.test bobpw
```

## 3. Trimiteti un mesaj SMTP

```bash
python3 scripts/send_mail_smtp.py \
  --smtp-host localhost \
  --smtp-port 587 \
  --user alice@example.test \
  --password alicepw \
  --to bob@example.test \
  --subject "Hello Bob" \
  --body "Sent from Alice to Bob" \
  --no-starttls
```

## 4. Cititi prin IMAP

```bash
python3 scripts/fetch_imap.py \
  --imap-host localhost \
  --imap-port 143 \
  --user bob@example.test \
  --password bobpw
```

## 5. Cititi prin POP3

```bash
python3 scripts/fetch_pop3.py \
  --pop3-host localhost \
  --pop3-port 110 \
  --user bob@example.test \
  --password bobpw
```

## 6. WebMail

Deschideti:

```text
http://localhost:8080
```

Login:

```text
bob@example.test / bobpw
```
