import socket
import threading

# -------------------------------------------------------------
# CONFIGURATIE LOAD BALANCER
# -------------------------------------------------------------

BACKENDS = [
    ("web1", 8000),
    ("web2", 8000),
    ("web3", 8000)
]

backend_index = 0

HOST = "0.0.0.0"
PORT = 8080
BUFFER_SIZE = 4096


def get_next_backend():
    """
    Selecteaza backend-ul urmator folosind round-robin.

    TODO pentru studenti:
    1. alegeti backend-ul curent din BACKENDS
    2. incrementati backend_index
    3. reveniti la 0 cand ati ajuns la finalul listei
    4. returnati backend-ul ales
    """
    global backend_index

    # TODO: implementati selectia round-robin
    # backend = ...
    # backend_index = ...
    # return backend

    return BACKENDS[0]


def read_http_response(backend_socket):
    """
    Citeste un raspuns HTTP simplu.

    Pentru acest seminar presupunem raspunsuri cu Content-Length,
    asa cum trimite python -m http.server pentru fisiere statice simple.
    """
    response = b""

    while b"\r\n\r\n" not in response:
        chunk = backend_socket.recv(BUFFER_SIZE)
        if not chunk:
            return response
        response += chunk

    headers, body = response.split(b"\r\n\r\n", 1)
    content_length = None

    for line in headers.decode("iso-8859-1").split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break

    if content_length is None:
        return response

    while len(body) < content_length:
        chunk = backend_socket.recv(BUFFER_SIZE)
        if not chunk:
            break
        body += chunk

    return headers + b"\r\n\r\n" + body


def forward_request_to_backend(request_data, backend_host, backend_port):
    """
    Trimite cererea bruta catre backend si intoarce raspunsul brut.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as backend_socket:
        backend_socket.settimeout(3)
        backend_socket.connect((backend_host, backend_port))
        backend_socket.sendall(request_data)

        return read_http_response(backend_socket)


def handle_client_connection(client_socket, client_addr):
    """
    Se ocupa de un singur client.
    """
    try:
        request_data = client_socket.recv(BUFFER_SIZE)

        if not request_data:
            return

        backend_host, backend_port = get_next_backend()
        print(f"[INFO] {client_addr} -> {backend_host}:{backend_port}")

        backend_response = forward_request_to_backend(
            request_data,
            backend_host,
            backend_port
        )

        client_socket.sendall(backend_response)

    except Exception as e:
        print("[ERROR]", e)

    finally:
        client_socket.close()


def main():
    print(f"[LB] Starting load balancer on port {PORT}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print("[LB] Listening for clients...")

        while True:
            client_socket, client_addr = server_socket.accept()
            print(f"[LB] Client connected: {client_addr}")

            thread = threading.Thread(
                target=handle_client_connection,
                args=(client_socket, client_addr)
            )
            thread.start()


if __name__ == "__main__":
    main()
