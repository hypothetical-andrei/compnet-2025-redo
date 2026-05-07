#!/usr/bin/env python3
import socket
import struct
import sys

"""
Seminar 7 – Sniffer simplu de pachete IPv4
...
"""

MAX_PACKETS = 50


def mac_addr(raw_mac: bytes) -> str:
    return ":".join(f"{b:02x}" for b in raw_mac)


def ipv4_addr(raw_ip: bytes) -> str:
    return ".".join(str(b) for b in raw_ip)


def parse_ethernet_header(data: bytes):
    dest_mac, src_mac, proto = struct.unpack("! 6s 6s H", data[:14])
    return mac_addr(dest_mac), mac_addr(src_mac), proto, data[14:]


def parse_ipv4_header(data: bytes):
    # 1. Primul octet contine versiunea (biti 7-4) si IHL (biti 3-0).
    #    IHL este numarul de cuvinte de 32 de biti din header;
    #    inmultim cu 4 pentru a obtine lungimea in octeti.
    version_ihl = data[0]
    version = version_ihl >> 4       # ar trebui sa fie 4 pentru IPv4
    ihl = (version_ihl & 0x0F) * 4  # lungimea header-ului in octeti (min 20)

    # 2. Extragem TTL, protocol si adresele IP din header.
    #    Formatul '! 8x B B 2x 4s 4s':
    #      !   – big-endian (network byte order)
    #      8x  – sarim peste octeti 1-8 (versiune/IHL, TOS, total length,
    #             identificare, flags, fragment offset)
    #      B   – TTL (1 octet)
    #      B   – protocol (1 octet): 1=ICMP, 6=TCP, 17=UDP
    #      2x  – sarim peste checksum (2 octeti)
    #      4s  – adresa sursa (4 octeti)
    #      4s  – adresa destinatie (4 octeti)
    ttl, proto, src, dst = struct.unpack('! 8x B B 2x 4s 4s', data[:20])

    # 3. Convertim adresele din bytes in string 'x.x.x.x'
    src_ip_str = ipv4_addr(src)
    dst_ip_str = ipv4_addr(dst)

    return src_ip_str, dst_ip_str, proto, ihl


def main():
    if len(sys.argv) < 2:
        print(f"Utilizare: sudo {sys.argv[0]} <INTERFATA>")
        print("Exemplu: sudo python3 packet_sniffer.py eth0")
        sys.exit(1)

    interface = sys.argv[1]

    try:
        sniffer = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    except PermissionError:
        print("Eroare: trebuie sa rulati cu privilegii de root (sudo).")
        sys.exit(1)

    try:
        sniffer.bind((interface, 0))
    except OSError as e:
        print(f"Eroare la bind pe interfata {interface}: {e}")
        sys.exit(1)

    print(f"[INFO] Pornim snifferul pe interfata {interface}")
    print(f"[INFO] Vom afisa maximum {MAX_PACKETS} pachete. Oprire cu Ctrl-C.\n")

    packet_count = 0

    try:
        while packet_count < MAX_PACKETS:
            raw_data, addr = sniffer.recvfrom(65535)
            packet_count += 1

            dest_mac, src_mac, eth_proto, payload = parse_ethernet_header(raw_data)

            if eth_proto == 0x0800:
                try:
                    src_ip, dst_ip, proto, ip_header_len = parse_ipv4_header(payload)
                except NotImplementedError:
                    print("parse_ipv4_header nu este inca implementata.")
                    break

                if proto == 6:
                    proto_str = "TCP"
                elif proto == 17:
                    proto_str = "UDP"
                elif proto == 1:
                    proto_str = "ICMP"
                else:
                    proto_str = f"ALT({proto})"

                print(f"[{packet_count}] {src_ip} -> {dst_ip}  proto={proto_str}")
                # Optional: puteti afisa si adresele MAC
                # print(f"    MAC: {src_mac} -> {dest_mac}")

    except KeyboardInterrupt:
        print("\n[INFO] Oprit de utilizator (Ctrl-C).")
    finally:
        sniffer.close()
        print("[INFO] Sniffer oprit.")


if __name__ == "__main__":
    main()