FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    iproute2 \
    iputils-ping \
    tcpdump \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

VOLUME ["/logs"]

CMD ["sleep", "infinity"]
