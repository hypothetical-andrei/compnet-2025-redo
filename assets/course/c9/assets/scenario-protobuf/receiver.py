#!/usr/bin/env python3
"""
receiver.py — asculta pe UDP, decodifica SensorBatch si afiseaza continutul.

Asteapta mesaje cu prefix de 4 octeti (lungime), extrage payload-ul
si il decodifica ca SensorBatch protobuf.
"""
import socket
import struct

import sensors_pb2

HOST = "127.0.0.1"
PORT = 9100
MAX_DGRAM = 65535

def decode_and_print(data: bytes) -> None:
    if len(data) < 4:
        print("[receiver] pachet prea scurt, ignorat")
        return

    length = struct.unpack(">I", data[:4])[0]
    payload = data[4:4 + length]

    if len(payload) < length:
        print(f"[receiver] payload incomplet: asteptat {length}B, primit {len(payload)}B")
        return

    batch = sensors_pb2.SensorBatch()
    batch.ParseFromString(payload)

    print(f"\n[receiver] SensorBatch station={batch.station_id!r} "
          f"({len(batch.readings)} readings, {length}B protobuf)")
    for r in batch.readings:
        print(f"  {r.sensor_id:12s}  {r.value:8.2f} {r.unit:8s}  ts={r.timestamp}")

def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[receiver] ascult pe {HOST}:{PORT} ...")

    try:
        while True:
            data, addr = sock.recvfrom(MAX_DGRAM)
            decode_and_print(data)
    except KeyboardInterrupt:
        print("\n[receiver] oprit")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
