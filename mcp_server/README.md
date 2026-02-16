# 🌎 MCP Server — ReservaT (Acceso Remoto via SSE)

Servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io) de **solo lectura** accesible por internet via **SSE (Server-Sent Events)**. Consulta todas las tablas de ReservaT desde cualquier agente de IA.

> ⚠️ La tabla `usuarios` está **EXCLUIDA** por seguridad.

## 🔧 Instalación

```bash
cd ms_experiencias/mcp_server

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

Variables de entorno:

| Variable      | Default     | Descripción                           |
| ------------- | ----------- | ------------------------------------- |
| `DB_USER`     | `postgres`  | Usuario de PostgreSQL                 |
| `DB_PASSWORD` | `postgres`  | Password de PostgreSQL                |
| `DB_HOST`     | `localhost` | Host de la BD                         |
| `DB_PORT`     | `5432`      | Puerto de la BD                       |
| `DB_NAME`     | `reservat`  | Nombre de la BD                       |
| `MCP_API_KEY` | —           | **Requerida.** Clave de autenticación |
| `MCP_HOST`    | `0.0.0.0`   | Host donde escucha el servidor        |
| `MCP_PORT`    | `8080`      | Puerto HTTP del servidor              |

## 🚀 Ejecutar

```bash
python server.py
# 🚀 Servidor disponible en http://0.0.0.0:8080/sse
```

### Despliegue en Producción

```bash
# Con Docker (ejemplo)
docker build -t mcp-reservat .
docker run -p 8080:8080 --env-file .env mcp-reservat

# Con systemd, PM2, o cualquier process manager
MCP_HOST=0.0.0.0 MCP_PORT=8080 python server.py
```

## 🔌 Conexión desde Clientes

### Desde un servicio remoto (via URL SSE)

La URL de conexión es:

```
http://<tu-ip-o-dominio>:8080/sse
```

### VS Code (local)

Crear `.vscode/mcp.json`:

```json
{
  "servers": {
    "reservat-db": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

### Claude Desktop

Edita `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "reservat-db": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

### n8n / Agentes Externos

Configura la conexión MCP con:

- **URL SSE:** `http://<tu-ip-o-dominio>:8080/sse`
- **Parámetro `api_key`:** incluirlo en cada llamada a tool

## 🛠️ Tools Disponibles (22 total)

Todas requieren `api_key` como primer parámetro.

### Proveedores

| Tool                 | Descripción                                   |
| -------------------- | --------------------------------------------- |
| `listar_proveedores` | Lista proveedores activos (paginado)          |
| `buscar_proveedores` | Busca por nombre/ciudad/país, filtra por tipo |

### Experiencias

| Tool                    | Descripción                      |
| ----------------------- | -------------------------------- |
| `listar_experiencias`   | Lista experiencias con proveedor |
| `consultar_experiencia` | Consulta por UUID                |

### Hoteles

| Tool              | Descripción                 |
| ----------------- | --------------------------- |
| `listar_hoteles`  | Lista hoteles con proveedor |
| `consultar_hotel` | Consulta por UUID           |

### Restaurantes

| Tool                    | Descripción                      |
| ----------------------- | -------------------------------- |
| `listar_restaurantes`   | Lista restaurantes con proveedor |
| `consultar_restaurante` | Consulta por UUID                |

### Servicios

| Tool                 | Descripción                              |
| -------------------- | ---------------------------------------- |
| `listar_servicios`   | Lista servicios (filtra por tipo/ciudad) |
| `consultar_servicio` | Consulta por UUID (incluye proveedor)    |
| `buscar_servicios`   | Busca por nombre/descripción/ciudad      |

### Fotos

| Tool                    | Descripción                |
| ----------------------- | -------------------------- |
| `listar_fotos_servicio` | Lista fotos de un servicio |

### Rutas

| Tool             | Descripción                    |
| ---------------- | ------------------------------ |
| `listar_rutas`   | Lista rutas turísticas activas |
| `consultar_ruta` | Consulta por UUID              |

### Viajes

| Tool              | Descripción                      |
| ----------------- | -------------------------------- |
| `listar_viajes`   | Lista viajes (filtra por estado) |
| `consultar_viaje` | Consulta por UUID (incluye ruta) |

### Transportes

| Tool                 | Descripción                             |
| -------------------- | --------------------------------------- |
| `listar_transportes` | Lista vehículos (filtra disponibilidad) |

### Mayoristas

| Tool                  | Descripción              |
| --------------------- | ------------------------ |
| `listar_mayoristas`   | Lista mayoristas activos |
| `consultar_mayorista` | Consulta por UUID        |

### Reservas

| Tool                | Descripción                        |
| ------------------- | ---------------------------------- |
| `listar_reservas`   | Lista reservas (filtra por estado) |
| `consultar_reserva` | Consulta por UUID                  |

### Fechas Bloqueadas

| Tool                       | Descripción                                   |
| -------------------------- | --------------------------------------------- |
| `listar_fechas_bloqueadas` | Lista fechas bloqueadas (filtra por servicio) |

## 🔒 Seguridad

- **API Key** requerida en todas las tools
- **Solo lectura** — no se exponen operaciones de escritura
- **Sin acceso a usuarios** — tabla excluida deliberadamente
- **Transporte SSE** — accesible via HTTP desde cualquier red
- Se recomienda usar **HTTPS** (nginx/Caddy como reverse proxy) en producción
