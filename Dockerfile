FROM python:3.11-slim

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Verificar que gunicorn se instaló
RUN which gunicorn && gunicorn --version

# Copiar el resto del código
COPY . .

# Crear usuario no root
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
