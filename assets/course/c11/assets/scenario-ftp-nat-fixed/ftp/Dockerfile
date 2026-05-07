FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ftp_server.py /app/ftp_server.py

EXPOSE 2121
EXPOSE 30000-30009

CMD ["python", "ftp_server.py"]
