import os
import logging
from http import HTTPStatus
from fastapi import FastAPI, Request, Response
from starlette.background import BackgroundTask
from starlette.types import Message
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from routes.mayorista_routes import mayorista

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
    title="Servicio de Mayoristas",
    description="API para gestión de mayoristas en ReservaT",
    debug=os.getenv("DEBUG", "false").lower() == "true",
    root_path="/api/v1",
    docs_url="/mayoristas/docs",
    openapi_url="/mayoristas/openapi.json"
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

add_pagination(app)
status_reasons = {x.value: x.name for x in list(HTTPStatus)}

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
        
    req_body = await request.body()
    await set_body(request, req_body)
    response = await call_next(request)

    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk

    informacion = {"Respuesta: " + status_reasons.get(response.status_code, "Unknown"), "URL: " + str(request.url),
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

# Incluir el router de mayoristas
app.include_router(mayorista, prefix="", tags=["Mayoristas"])
