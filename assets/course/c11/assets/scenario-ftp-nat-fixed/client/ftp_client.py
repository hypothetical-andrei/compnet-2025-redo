from __future__ import annotations

from ftplib import FTP, all_errors
import os
import socket
import subprocess
import time

HOST = os.environ.get("FTP_HOST", "ftp-server")
PORT = int(os.environ.get("FTP_PORT", "2121"))


def show_network_debug():
    print("Client routes:", flush=True)
    subprocess.run(["ip", "route"], check=False)

    try:
        print(f"{HOST} resolves to {socket.gethostbyname(HOST)}", flush=True)
    except OSError as err:
        print(f"Could not resolve {HOST}: {err}", flush=True)


def connect_with_retry(retries=20, delay=1):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            ftp = FTP()
            ftp.connect(HOST, PORT, timeout=10)
            return ftp
        except all_errors as err:
            last_error = err
            print(f"FTP not ready, attempt {attempt}/{retries}: {err}", flush=True)
            time.sleep(delay)

    raise RuntimeError(f"Could not connect to FTP server at {HOST}:{PORT}") from last_error


def run(passive: bool):
    print("-" * 60, flush=True)
    print(f"Trying FTP with passive={passive}", flush=True)
    show_network_debug()

    ftp = connect_with_retry()
    ftp.login("student", "student")
    ftp.set_pasv(passive)

    print("PWD =", ftp.pwd(), flush=True)
    print("LIST:", flush=True)
    ftp.retrlines("LIST")

    ftp.quit()
    print(f"passive={passive} completed", flush=True)


if __name__ == "__main__":
    run(passive=True)

    try:
        run(passive=False)
    except Exception as err:
        print("Active mode failed as expected in a NAT/firewall topology:", err, flush=True)
