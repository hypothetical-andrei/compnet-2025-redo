import argparse
import socket
import sys
import threading


def forward_stdin(sock, addr=None, udp=False):
    while True:
        data = sys.stdin.buffer.readline()
        if not data:
            break

        if udp:
            sock.sendto(data, addr)
        else:
            sock.sendall(data)


def receive(sock, udp=False):
    while True:
        try:
            if udp:
                data, _ = sock.recvfrom(4096)
            else:
                data = sock.recv(4096)
        except:
            break

        if not data:
            break

        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()


def tcp_server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", port))
    s.listen(1)

    conn, addr = s.accept()
    print(f"Connection from {addr}", file=sys.stderr)

    threading.Thread(target=receive, args=(conn,), daemon=True).start()
    forward_stdin(conn)


def tcp_client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    threading.Thread(target=receive, args=(s,), daemon=True).start()
    forward_stdin(s)


def udp_server(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", port))

    addr = None

    def recv_loop():
        nonlocal addr
        while True:
            data, addr = s.recvfrom(4096)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()

    threading.Thread(target=recv_loop, daemon=True).start()

    while True:
        data = sys.stdin.buffer.readline()
        if addr:
            s.sendto(data, addr)


def udp_client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (host, port)

    threading.Thread(target=receive, args=(s, True), daemon=True).start()
    forward_stdin(s, addr, True)


def main():
    parser = argparse.ArgumentParser(description="pycat")
    parser.add_argument("-l", action="store_true", help="listen mode")
    parser.add_argument("-u", action="store_true", help="udp mode")
    parser.add_argument("-p", type=int, help="port (used in listen mode)")
    parser.add_argument("host", nargs="?")
    parser.add_argument("port", nargs="?", type=int)

    args = parser.parse_args()

    if args.l:
        if not args.p:
            print("Listen mode requires -p", file=sys.stderr)
            sys.exit(1)

        if args.u:
            udp_server(args.p)
        else:
            tcp_server(args.p)

    else:
        if not args.host or not args.port:
            print("Usage: pycat host port", file=sys.stderr)
            sys.exit(1)

        if args.u:
            udp_client(args.host, args.port)
        else:
            tcp_client(args.host, args.port)


if __name__ == "__main__":
    main()