FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir dnslib==0.9.24

COPY dns_server.py /app/dns_server.py

EXPOSE 5353/udp

CMD ["python", "-u", "dns_server.py"]