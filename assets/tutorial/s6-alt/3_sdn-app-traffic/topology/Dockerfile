FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openvswitch-switch \
    iproute2 \
    iputils-ping \
    tcpdump \
    net-tools \
    python3 \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Scripturile Python sunt copiate in /apps — disponibile in toate namespace-urile
# via 'host hX python3 /apps/tcp_server.py ...'
COPY tcp_server.py /apps/tcp_server.py
COPY tcp_client.py /apps/tcp_client.py
COPY udp_server.py /apps/udp_server.py
COPY udp_client.py /apps/udp_client.py

CMD ["/entrypoint.sh"]
