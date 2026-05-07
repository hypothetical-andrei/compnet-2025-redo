FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY provision.py /app/provision.py
COPY plan.json /app/plan.json

CMD ["python", "provision.py"]