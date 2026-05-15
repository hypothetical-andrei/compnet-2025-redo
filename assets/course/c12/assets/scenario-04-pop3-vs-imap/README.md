# Scenario 4 - POP3 vs IMAP operational

## Obiective

* compararea modelelor operationale POP3 si IMAP
* observarea sincronizarii IMAP
* observarea modelului download-and-delete POP3

## 1. Porniti stack-ul

```bash
docker compose up -d
docker exec -it dms setup email add alice@example.test alicepw
```

## 2. Trimiteti doua mesaje

```bash
python3 scripts/send_mail_smtp.py \
  --smtp-host localhost \
  --smtp-port 587 \
  --user alice@example.test \
  --password alicepw \
  --to alice@example.test \
  --subject "msg1" \
  --body "First message"

python3 scripts/send_mail_smtp.py \
  --smtp-host localhost \
  --smtp-port 587 \
  --user alice@example.test \
  --password alicepw \
  --to alice@example.test \
  --subject "msg2" \
  --body "Second message"
```

## 3. Citire IMAP

```bash
  python3 scripts/fetch_imap.py \
  --imap-host localhost \
  --imap-port 143 \
  --user alice@example.test \
  --password alicepw \
  --search ALL
```

## 4. Citire POP3

```bash
python3 scripts/fetch_pop3.py \
  --pop3-host localhost \
  --pop3-port 110 \
  --user alice@example.test \
  --password alicepw
```

## 5. Bonus: stergere POP3

```bash
  python3 scripts/fetch_pop3_delete.py \
  --pop3-host localhost \
  --pop3-port 110 \
  --user alice@example.test \
  --password alicepw
```

Verificati apoi din WebMail sau IMAP daca mesajul mai exista.

## 6. Intrebari

1. Ce se intampla cu mesajele in IMAP?
2. Ce se intampla cu mesajele in POP3?
3. Care protocol este mai potrivit pentru mai multe device-uri?
4. Care protocol este mai simplu pentru un client minimal?
