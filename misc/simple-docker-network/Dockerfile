FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y \
        iproute2 \
        iputils-ping \
        net-tools \
        netcat-openbsd \
        tcpdump \
    && rm -rf /var/lib/apt/lists/*

CMD ["bash"]
