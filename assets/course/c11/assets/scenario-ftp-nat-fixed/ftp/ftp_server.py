from __future__ import annotations

import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


FTP_PORT = int(os.environ.get("FTP_PORT", "2121"))
PASSIVE_PORTS = range(30000, 30010)
DATA_DIR = os.environ.get("FTP_DATA_DIR", "/data")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    authorizer = DummyAuthorizer()
    authorizer.add_user("student", "student", DATA_DIR, perm="elradfmwMT")
    authorizer.add_anonymous(DATA_DIR, perm="elr")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.passive_ports = PASSIVE_PORTS

    address = ("0.0.0.0", FTP_PORT)
    server = FTPServer(address, handler)

    print(f"FTP server listening on {address}", flush=True)
    print("Passive ports: 30000-30009", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
