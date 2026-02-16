FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y sqlalchemy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Configurar entorno
ENV PYTHONUNBUFFERED=1

# Copiar y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Limpiar dependencias de construcción
RUN apt-get purge -y gcc && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Copiar el resto del código
COPY . .

# El servidor arranca en el puerto 8080 por defecto (configurable via MCP_PORT)
EXPOSE 8080

# Comando para iniciar el servidor MCP usando SSE
CMD ["python", "server.py"]
