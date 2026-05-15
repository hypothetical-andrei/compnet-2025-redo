# Scenario 5 - WebMail architecture

## Obiective

* intelegerea WebMail ca aplicatie HTTP
* observarea relatiei Browser -> HTTP -> IMAP/SMTP
* observarea separarii dintre UI si protocoalele de e-mail

## 1. Porniti stack-ul

```bash
docker compose up -d
docker exec -it dms setup email add alice@example.test alicepw
```

## 2. Accesati Roundcube

```text
http://localhost:8080
```

Login:

```text
alice@example.test / alicepw
```

## 3. Trimiteti un mesaj din WebMail

Din interfata Roundcube:

* compuneti un mesaj
* trimiteti catre alice@example.test
* cititi mesajul primit

## 4. Test comparativ: Python -> WebMail

```bash
python3 scripts/send_mail_smtp.py \
  --smtp-host localhost \
  --smtp-port 587 \
  --user alice@example.test \
  --password alicepw \
  --to alice@example.test \
  --subject "Python to WebMail" \
  --body "This should appear in Roundcube"
```

Verificati apoi mesajul in WebMail. 

Mesajele trimise folosind `send_mail_smtp.py` apar în Inbox-ul destinatarului, dar NU apar automat în folderul „Sent” al expeditorului.

SMTP se ocupă doar de transportul mesajului între client și server. Gestionarea folderelor precum „Sent”, „Drafts” sau „Archive” este realizată separat, de obicei prin IMAP.

Clienții WebMail (precum Roundcube) sau clienții desktop salvează explicit o copie a mesajului în folderul „Sent”.

## 5. Ce se intampla in spate

Browserul comunica prin HTTP/HTTPS cu WebMail.

WebMail comunica mai departe cu:

* SMTP submission pentru trimitere
* IMAP pentru citire
* mailbox-ul serverului pentru stocare

## 6. Intrebari

1. De ce browserul nu vorbeste direct SMTP?
2. De ce browserul nu vorbeste direct IMAP?
3. Ce avantaj are WebMail fata de un client local?
4. Ce dezavantaje apar fata de un client local?
