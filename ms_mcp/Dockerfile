FROM node:20-slim

# Usuario no-root
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json* ./

# Instalar dependencias
RUN npm ci 2>/dev/null || npm install

# Copiar código fuente
COPY . .

# Cambiar a usuario no-root
RUN chown -R app:app /app
USER app

# Exponer el puerto
EXPOSE 8020

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://localhost:8020/healthchecker').then(r => r.ok ? process.exit(0) : process.exit(1)).catch(() => process.exit(1))"

# Ejecutar con tsx
CMD ["npx", "tsx", "src/index.ts"]
