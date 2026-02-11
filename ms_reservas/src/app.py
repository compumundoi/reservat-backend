import logging
from http import HTTPStatus
from fastapi import FastAPI, Request, Response
from starlette.background import BackgroundTask
from starlette.types import Message
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from routes.reservas_routes import reservas


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
    title="Servicio de reservas para servicios",
    description="API de gestión para las reservas de los servicios en ReservaT",
    debug=True,
    root_path="/api/v1",
    docs_url="/reservas/docs",
    openapi_url="/reservas/openapi.json"
)

# Agrega aquí tu dominio del frontend
origins = [
    "https://dashboard.reservatonline.com",
    "http://dashboard.reservatonline.com:8000",
    "https://proveedores.reservatonline.com",
    "https://reservatonline.com",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:5173",  # opcional para desarrollo local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # O usa ["*"] si quieres permitir todo (no recomendado en producción)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Incluir el router de reservas 
app.include_router( reservas, prefix="", tags=["Reserva de servicios"])
