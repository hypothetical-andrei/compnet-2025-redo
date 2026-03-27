# Introducere: Rutare pe trei routere (topologie triunghi)

În această secțiune vom folosi Mininet pentru a crea o topologie formată din trei routere Linux și două hosturi. Scopul este să observăm cum rutarea statică determină calea traficului și cum modificarea rutelor redirecționează traficul în timp real.

## Topologia

```
h1
 |
r1 ----- r2
 \       /
  \     /
    r3
    |
    h3
```

Topologia conține:
- **h1** — host sursă, conectat la r1
- **h3** — host destinație, conectat la r3
- **r1, r2, r3** — routere Linux (noduri Mininet cu IP forwarding activat)
- **3 linkuri router-router**: r1–r2, r2–r3, r1–r3

---

## Schema de adresare

Folosim subrețele /30 pentru fiecare legătură punct-la-punct:

| Legătură    | Subnet         | IP stânga   | IP dreapta  |
|-------------|----------------|-------------|-------------|
| h1 ↔ r1     | 10.0.1.0/30    | h1: 10.0.1.2 | r1: 10.0.1.1 |
| r1 ↔ r2     | 10.0.12.0/30   | r1: 10.0.12.1 | r2: 10.0.12.2 |
| r2 ↔ r3     | 10.0.23.0/30   | r2: 10.0.23.1 | r3: 10.0.23.2 |
| r1 ↔ r3     | 10.0.13.0/30   | r1: 10.0.13.1 | r3: 10.0.13.2 |
| r3 ↔ h3     | 10.0.3.0/30    | r3: 10.0.3.1 | h3: 10.0.3.2 |

---

## Starea inițială

La pornirea topologiei, sunt pre-configurate doar rutele necesare pentru calea **h1 → r1 → r2 → r3 → h3**:

| Nod | Rută adăugată | Via |
|-----|---------------|-----|
| h1  | default       | 10.0.1.1 (r1) |
| h3  | default       | 10.0.3.1 (r3) |
| r1  | 10.0.3.0/30   | 10.0.12.2 (r2) |
| r2  | 10.0.1.0/30   | 10.0.12.1 (r1) |
| r2  | 10.0.3.0/30   | 10.0.23.2 (r3) |
| r3  | 10.0.1.0/30   | 10.0.23.1 (r2) |

Legătura r1–r3 există fizic, dar **nu este folosită în rutare** — nu există rute care să trimită trafic prin ea.

---

## Ce vom face în exerciții

1. Verificăm că h1 poate ajunge la h3 prin calea r1→r2→r3 (calea inițială)
2. Adăugăm rute care activează legătura directă r1→r3
3. Observăm cu `traceroute` că traficul continuă să meargă prin r2 (metrica e egală, kernel-ul alege prima rută instalată)
4. Ștergem ruta r1→r2 de pe r1
5. Observăm că traficul se mută automat pe calea r1→r3→r2→h3

Aceasta ilustrează principiul fundamental al rutării statice: **traficul urmează întotdeauna cea mai specifică rută disponibilă în tabela de rutare**.