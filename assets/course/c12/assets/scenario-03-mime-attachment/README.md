# Scenario 3 - MIME multipart + attachment

## Obiective

* intelegerea MIME multipart
* observarea boundary-urilor MIME
* observarea attachment-urilor base64

## 1. Porniti stack-ul

```bash
docker compose up -d
docker exec -it dms setup email add alice@example.test alicepw
```

## 2. Trimiteti attachment-ul

```bash
python3 scripts/send_attachment_smtp.py \
  --smtp-host localhost \
  --smtp-port 587 \
  --user alice@example.test \
  --password alicepw \
  --to alice@example.test \
  --file sample.txt
```

## 3. Deschideti mesajul in WebMail

```text
http://localhost:8080
```

Login:

```text
alice@example.test / alicepw
```

Observati:

* attachment-ul
* numele fisierului
* tipul MIME

## 4. Inspectati sursa mesajului

Identificati:

* MIME-Version
* Content-Type: multipart/mixed
* boundary
* Content-Disposition: attachment
* Content-Transfer-Encoding: base64

## 5. Decodare manuala

Copiati corpul base64 al attachment-ului intr-un fisier si rulati:

```bash
base64 -d encoded.txt
```

## 6. Intrebari

1. De ce SMTP original nu putea transporta fisiere binare?
2. Ce rol are boundary?
3. De ce este folosit base64?
4. Care este diferenta dintre multipart/mixed si multipart/alternative?
