FROM python:3.12-slim

RUN pip install --no-cache-dir "os-ken==3.1.0" \
 && osken-manager --version

WORKDIR /app
COPY controller.py .

EXPOSE 6633

CMD ["osken-manager", "controller.py"]
