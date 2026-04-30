#!/usr/bin/env python3
import socket
import sys
import time

"""
Seminar 7 – UDP Spray helper

Trimite câte un pachet UDP spre fiecare port dintr-un interval dat.
Folosit pentru a testa detectarea "UDP spray" din mini_ids.py.

Utilizare:
    python3 udp_spray.py <HOST> <START_PORT> <END_PORT> [DELAY_MS]

Exemple:
    python3 udp_spray.py 10.0.10.2 6000 6030
    python3 udp_spray.py 10.0.10.2 6000 6030 50
"""


def main():
    if len(sys.argv) < 4:
        print(f"Utilizare: {sys.argv[0]} <HOST> <START_PORT> <END_PORT> [DELAY_MS]")
        print("Exemplu: python3 udp_spray.py 10.0.10.2 6000 6030 50")
        sys.exit(1)

    host = sys.argv[1]
    start_port = int(sys.argv[2])
    end_port = int(sys.argv[3])
    delay_s = float(sys.argv[4]) / 1000.0 if len(sys.argv) >= 5 else 0.05

    print(f"[UDP SPRAY] Trimit pachete UDP catre {host} porturile {start_port}-{end_port}")
    print(f"[UDP SPRAY] Delay intre pachete: {delay_s*1000:.0f}ms")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        for port in range(start_port, end_port + 1):
            try:
                s.sendto(b"spray", (host, port))
                print(f"[UDP SPRAY] -> {host}:{port}")
            except Exception as e:
                print(f"[UDP SPRAY] Eroare la portul {port}: {e}")
            time.sleep(delay_s)

    print("[UDP SPRAY] Terminat.")


if __name__ == "__main__":
    main()
