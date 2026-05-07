#!/usr/bin/env python3
"""
sender.py — codifica SensorBatch si trimite peste UDP.

Fiecare mesaj este prefixat cu 4 octeti (big-endian) care indica
lungimea payload-ului protobuf. Receptorul stie astfel cat sa citeasca.
"""
import socket
import struct
import time

import sensors_pb2

HOST = "127.0.0.1"
PORT = 9100

def make_batch(station_id: str, n: int) -> sensors_pb2.SensorBatch:
    batch = sensors_pb2.SensorBatch()
    batch.station_id = station_id

    now = int(time.time())
    sensors = [
        ("temp-1",  20.4 + n * 0.1, "celsius"),
        ("press-1", 1013.2 - n * 0.5, "hpa"),
        ("hum-1",   55.0 + n * 0.3, "pct"),
    ]
    for sid, val, unit in sensors:
        r = batch.readings.add()
        r.sensor_id = sid
        r.timestamp = now
        r.value = round(val, 2)
        r.unit = unit

    return batch

def send_batch(sock: socket.socket, batch: sensors_pb2.SensorBatch) -> None:
    payload = batch.SerializeToString()
    # prefix: 4 octeti lungime
    header = struct.pack(">I", len(payload))
    sock.sendto(header + payload, (HOST, PORT))
    print(f"[sender] trimis batch station={batch.station_id!r} "
          f"readings={len(batch.readings)} payload={len(payload)}B")

def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for i in range(5):
        batch = make_batch("statia-nord", i)
        send_batch(sock, batch)
        time.sleep(0.5)

    sock.close()
    print("[sender] done")

if __name__ == "__main__":
    main()
