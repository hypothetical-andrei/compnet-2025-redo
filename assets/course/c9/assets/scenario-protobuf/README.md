### Scenario: Protocol binar cu Protocol Buffers

### Obiectiv
- Definim un protocol cu doua tipuri de mesaje in `.proto`
- Codificam date ca SensorBatch si le trimitem peste UDP
- Decodificam la receptor si afisam campurile structurate
- Observam ca schema `.proto` este necesara la ambele capete

### Cerinte
- python3
- pip3 (pentru instalarea bibliotecii protobuf)
- Conexiune internet (doar la primul setup, pentru pip)

### Structura fisierelor
```
sensors.proto      # definitia schemei (sursa de adevar)
sender.py          # codifica SensorBatch si trimite UDP
receiver.py        # primeste UDP, decodifica si afiseaza
setup.sh           # instaleaza dependentele si compileaza .proto
run.sh             # porneste receiver + sender automat
```

### Cum rulezi

1) Prima rulare — compileaza schema
```
chmod +x setup.sh run.sh
./setup.sh
```

Acest pas genereaza `sensors_pb2.py` din `sensors.proto`.
Fara acest fisier, sender si receiver nu stiu cum sa codifice/decodifice.

2) Ruleaza scenariul
```
./run.sh
```

### Output asteptat
```
[receiver] ascult pe 127.0.0.1:9100 ...
[sender] trimis batch station='statia-nord' readings=3 payload=67B
[receiver] SensorBatch station='statia-nord' (3 readings, 67B protobuf)
  temp-1        20.40 celsius  ts=1718000000
  press-1     1013.20 hpa      ts=1718000000
  hum-1         55.00 pct      ts=1718000000
...
```

### Ce observi
- Schema `.proto` defineste structura inainte de orice transfer
- Payload-ul binar este compact (comparati cu JSON echivalent)
- Fara schema, bytes-ii primiti sunt imposibil de interpretat
- Cele doua tipuri de mesaje (SensorReading, SensorBatch) sunt compozabile

### Experiment optional
- Deschide `sensors_pb2.py` generat si observa codul Python produs din schema
- Modifica un camp in `.proto`, ruleaza din nou `./setup.sh` si observa eroarea
  daca sender si receiver nu sunt sincronizati pe aceeasi schema
