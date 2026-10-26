import os
import logging
from http import HTTPStatus
from fastapi import FastAPI, Request, Response
from starlette.background import BackgroundTask
from starlette.types import Message
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.fotos_routes import fotos
from config.s3 import TAMANO_MAXIMO_BYTES

# Margen sobre la imagen para los campos de texto y separadores del formulario.
LIMITE_MULTIPART_BYTES = TAMANO_MAXIMO_BYTES + 64 * 1024


# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d- %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configurar el logger de la aplicación
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Servicio de fotos para servicios",
    description="API de gestión para las fotos de los servicios en ReservaT",
    debug=os.getenv("DEBUG", "false").lower() == "true",
    root_path="/api/v1",
    docs_url="/fotos/docs",
    openapi_url="/fotos/openapi.json"
)

# Orígenes permitidos para CORS
origins = [
    # Producción
    "https://reservatonline.com",
    "https://www.reservatonline.com",
    "https://dashboard.reservatonline.com",
    "https://proveedores.reservatonline.com",
    # Desarrollo local
    "http://reservatonline.com:8000",
    "http://dashboard.reservatonline.com:8000",
    "http://proveedores.reservatonline.com:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:5173",
]

# Configuración de CORS se movió abajo para ser el middleware más externo

add_pagination(app)
status_reasons = {x.value: x.name for x in list(HTTPStatus)}

# Importar rutas después de crear la aplicación


def log_info(req_body, res_body, informacion):
    logging.info(req_body)
    logging.info(res_body)
    logging.info(informacion)

async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {'type': 'http.request', 'body': body}

    request._receive = receive

@app.middleware('http')
async def some_middleware(request: Request, call_next):
    # No procesar preflights de CORS en el middleware de logging
    if request.method == "OPTIONS":
        return await call_next(request)
        
    if request.headers.get("content-type", "").startswith("multipart/form-data"):
        # Las subidas no se cargan enteras en memoria ni se escriben al log.
        # Se rechazan antes de leerlas si declaran mas de lo permitido.
        largo = request.headers.get("content-length", "")
        if not largo.isdigit() or int(largo) > LIMITE_MULTIPART_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": f"La imagen supera el maximo de {TAMANO_MAXIMO_BYTES // (1024 * 1024)} MB"},
            )
        req_body = b"<multipart omitido del log>"
    else:
        req_body = await request.body()
        await set_body(request, req_body)
    response = await call_next(request)

    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk

    informacion = {"Respuesta: " + status_reasons.get(response.status_code), "URL: " + request.url.path,
                   "Metodo: " + request.method,
                   "Headers: " + str(request.headers)}

    task = BackgroundTask(log_info, req_body, res_body, informacion)
    return Response(content=res_body, status_code=response.status_code,
                    headers=dict(response.headers), media_type=response.media_type, background=task)

# Configurar CORS como el middleware más externo (agregado al final)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir el router de fotos 
app.include_router( fotos, prefix="", tags=["Foto de servicios"])
