from ftplib import FTP
import os
import socket
import time

HOST = os.environ.get("FTP_HOST", "ftp")
PORT = int(os.environ.get("FTP_PORT", "2121"))


def connect_with_retry(retries=20, delay=1):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            ftp = FTP()
            ftp.connect(HOST, PORT, timeout=10)
            return ftp
        except (ConnectionRefusedError, socket.timeout, OSError) as err:
            last_error = err
            print(f"FTP not ready yet, attempt {attempt}/{retries}: {err}", flush=True)
            time.sleep(delay)

    raise RuntimeError(f"Could not connect to FTP server at {HOST}:{PORT}") from last_error


def run(passive=True):
    ftp = connect_with_retry()
    ftp.login("student", "student")
    ftp.set_pasv(passive)

    print("PASSIVE =", passive)
    print("PWD =", ftp.pwd())
    print("LIST:")
    ftp.retrlines("LIST")

    data = b"hello ftp\n"
    with open("hello.txt", "wb") as f:
        f.write(data)

    with open("hello.txt", "rb") as f:
        ftp.storbinary("STOR hello.txt", f)

    with open("hello-down.txt", "wb") as f:
        ftp.retrbinary("RETR hello.txt", f.write)

    ftp.quit()
    print("done")


if __name__ == "__main__":
    run(passive=True)
    run(passive=False)