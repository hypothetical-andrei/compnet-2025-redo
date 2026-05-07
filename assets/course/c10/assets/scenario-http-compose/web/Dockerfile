FROM python:3.12-slim

WORKDIR /app

COPY index.html /app/index.html
COPY server.py /app/server.py

EXPOSE 8000

CMD ["python", "server.py"]