FROM python:3.11-slim

WORKDIR /app

# Set PYTHONPATH to include the src directory
ENV PYTHONPATH=/app/src

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Configurar entorno
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Limpiar dependencias del sistema
RUN apt-get purge -y gcc && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY . .

# Exponer el puerto
EXPOSE 8000

# Configurar uvicorn para producción
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
