FROM python:3.11-slim

# Instalăm os-ken (fork al ryu pentru OpenFlow)
RUN pip install --no-cache-dir os-ken

WORKDIR /app

# Aplicația controller va fi montată ca volum
CMD ["osken-manager", "/app/sdn_controller.py"]
