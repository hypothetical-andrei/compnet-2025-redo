# Observarea handshake-ului TLS cu openssl

## Obiectiv

- Să vezi cum arată un handshake TLS (mesaje, versiune, cipher)
- Să vezi certificatul (subject/issuer) și verificarea lui
- Să înțelegi diferența dintre „TCP connect" și „TLS handshake"
- Să captezi și să inspectezi traficul TLS în Wireshark

## Cerințe

- Linux
- `openssl` (`sudo apt install openssl`)
- `wireshark` sau `tshark` — opțional, pentru captura de trafic (`sudo apt install wireshark`)

## Rulare

### 1. Generează certificat self-signed

```bash
./gen_certs.sh
```

Creează `certs/cert.pem` și `certs/key.pem` — certificat RSA 2048-bit valabil 7 zile, emis pentru `CN=localhost`.

### 2. Pornește serverul TLS (Terminal 1)

```bash
./run_server.sh
```

Pornește `openssl s_server` pe portul **9443** cu TLS 1.3. Modul `-www` face serverul să răspundă cu o pagină de status la orice request HTTP.

### 3. Conectează clientul TLS (Terminal 2)

```bash
./run_client.sh
```

Rulează `openssl s_client` și afișează detaliile handshake-ului, apoi închide conexiunea.

### Ce observi în output-ul clientului

```
Protocol  : TLSv1.3
Cipher    : TLS_AES_256_GCM_SHA384
Server certificate subject: CN=localhost
Verify return code: 18 (self-signed certificate)
```

- **Protocol / Cipher** — ce a negociat handshake-ul
- **Verify return code 18** — certificatul nu e semnat de un CA de încredere (self-signed); conexiunea se stabilește totuși, dar un browser real ar afișa avertisment
- **Certificate chain** — cu `-showcerts` vezi certificatul în format PEM; îl poți decoda cu `openssl x509 -in certs/cert.pem -text -noout`

---

## Captură Wireshark

### De ce traficul apare ca „Application Data" (criptat)?

TLS 1.3 criptează aproape tot, inclusiv certificatul și majoritatea mesajelor de handshake (după `Server Hello`). Wireshark poate totuși să identifice **tipul** fiecărui record TLS și să afișeze structura handshake-ului, chiar dacă nu poate decripta conținutul fără cheia de sesiune.

### Pas 1 — pornește captura

**Interfața**: traficul dintre client și server trece pe `lo` (loopback), nu pe `eth0`.

```bash
# Varianta GUI — selectează interfața "Loopback: lo" la start
wireshark &

# Varianta CLI
sudo tshark -i lo -w capture.pcap
```

### Pas 2 — filtru de captură (în timp real)

În câmpul de filtru Wireshark aplică:

```
tcp.port == 9443
```

Aceasta limitează afișarea la conexiunile pe portul serverului nostru.

### Pas 3 — rulează scenariul

Cu captura activă, rulează în ordine:
1. `./run_server.sh` (dacă nu e deja pornit)
2. `./run_client.sh`

### Pas 4 — ce să urmărești în Wireshark

| Nr. | Direcție | Protocol | Conținut vizibil |
|-----|----------|----------|-----------------|
| 1–3 | h1 ↔ h2 | TCP | Three-way handshake (`SYN`, `SYN-ACK`, `ACK`) |
| 4   | client → server | TLSv1.3 | `Client Hello` — versiuni suportate, cipher suites, extensii (`SNI: localhost`) |
| 5   | server → client | TLSv1.3 | `Server Hello` — cipher ales, key share |
| 6   | server → client | TLSv1.3 | `Change Cipher Spec` + `Application Data` (certificat + Finished, deja criptate) |
| 7   | client → server | TLSv1.3 | `Change Cipher Spec` + `Application Data` (Finished) |
| 8+  | ambele  | TLSv1.3 | `Application Data` — payload HTTP criptat |

> **Notă TLS 1.3 vs 1.2**: În TLS 1.2, `Certificate`, `Server Hello Done` și `Certificate Verify` apar ca mesaje separate, vizibile în clar în Wireshark. În TLS 1.3 acestea sunt criptate după `Server Hello` — de aceea scripturile folosesc `-tls1_3` explicit, pentru a demonstra comportamentul modern.

### Pas 5 — decriptare opțională cu SSLKEYLOGFILE

Poți forța clientul să scrie cheile de sesiune într-un fișier pe care Wireshark îl poate folosi pentru a decripta traficul:

```bash
# Terminal 2 — în loc de ./run_client.sh, rulează direct:
SSLKEYLOGFILE=./sslkeys.log openssl s_client \
  -connect 127.0.0.1:9443 \
  -tls1_3 \
  -servername localhost \
  -showcerts \
  </dev/null
```

Apoi în Wireshark:
1. **Edit → Preferences → Protocols → TLS**
2. Câmpul **(Pre)-Master-Secret log filename** → selectează `sslkeys.log`
3. Pachetele `Application Data` se vor decripta și vor apărea ca `HTTP`

Aceasta ilustrează de ce `SSLKEYLOGFILE` trebuie protejat — cine are fișierul poate decripta întreaga sesiune.

---

## Curățare

```bash
./cleanup.sh
```

Șterge directorul `certs/`.