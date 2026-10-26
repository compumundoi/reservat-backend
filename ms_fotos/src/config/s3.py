import logging
import os
import uuid

import boto3

logger = logging.getLogger()

# app.py configura el log en DEBUG; en ese nivel botocore escribe las
# cabeceras firmadas, con el Access Key ID incluido.
for _nombre in ("boto3", "botocore", "s3transfer", "urllib3"):
    logging.getLogger(_nombre).setLevel(logging.WARNING)

# Tipos aceptados: la extension sale del contenido real del archivo, no del
# nombre que manda el cliente.
FIRMAS_IMAGEN = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

TAMANO_MAXIMO_BYTES = int(os.getenv("FOTO_TAMANO_MAXIMO_MB", "5")) * 1024 * 1024


class AlmacenamientoNoConfigurado(Exception):
    """Falta S3_BUCKET: el servicio no puede subir archivos."""


def detectar_tipo_imagen(contenido: bytes):
    """Devuelve el content-type segun los bytes iniciales, o None si no es imagen soportada."""
    if contenido.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if contenido.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if contenido[:4] == b"RIFF" and contenido[8:12] == b"WEBP":
        return "image/webp"
    if contenido[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    return None


class AlmacenamientoS3:
    """Sube y borra imagenes en el bucket de fotos.

    Las credenciales las resuelve boto3 por su cadena estandar
    (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY o el rol de la instancia),
    asi que nunca pasan por el codigo.
    """

    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET", "").strip()
        self.region = os.getenv("AWS_REGION", "us-east-1").strip()
        # El bucket puede ser compartido con otros sistemas: todo lo de
        # ReservaT vive bajo este prefijo y nada fuera de el se toca.
        self.prefijo = os.getenv("S3_PREFIX", "reservat/fotos").strip("/")
        # Endpoint alterno para MinIO u otro S3 compatible en desarrollo.
        self.endpoint = os.getenv("S3_ENDPOINT_URL", "").strip() or None
        self.url_publica = os.getenv("S3_PUBLIC_BASE_URL", "").strip().rstrip("/")
        self._cliente = None

    @property
    def configurado(self) -> bool:
        return bool(self.bucket)

    def _client(self):
        if not self.configurado:
            raise AlmacenamientoNoConfigurado()
        if self._cliente is None:
            self._cliente = boto3.client("s3", region_name=self.region, endpoint_url=self.endpoint)
        return self._cliente

    def _url_de(self, clave: str) -> str:
        if self.url_publica:
            return f"{self.url_publica}/{clave}"
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{clave}"

    def subir(self, contenido: bytes, content_type: str, servicio_id) -> tuple[str, str]:
        """Sube la imagen y devuelve (clave, url publica)."""
        extension = FIRMAS_IMAGEN[content_type]
        clave = f"{self.prefijo}/{servicio_id}/{uuid.uuid4()}.{extension}"
        self._client().put_object(
            Bucket=self.bucket,
            Key=clave,
            Body=contenido,
            ContentType=content_type,
        )
        return clave, self._url_de(clave)

    def borrar(self, clave: str) -> None:
        """Borra un objeto; se usa para no dejar huerfanos si falla la BD."""
        try:
            self._client().delete_object(Bucket=self.bucket, Key=clave)
        except Exception as e:
            logger.error(f"No se pudo borrar {clave} del bucket: {str(e)}")

    def clave_de(self, url: str):
        """Devuelve la clave si la URL esta bajo el prefijo de ReservaT, o None.

        Exigir el prefijo, y no solo el bucket, evita borrar archivos de otro
        sistema que comparta el bucket aunque una foto apunte a ellos.
        """
        if not self.configurado or not url:
            return None
        base = self._url_de(f"{self.prefijo}/")
        if url.startswith(base) and len(url) > len(base):
            return url[len(self._url_de("")):]
        return None

    def borrar_por_url(self, url: str) -> None:
        """Borra el archivo de una foto eliminada. Las URLs externas no se tocan."""
        clave = self.clave_de(url)
        if clave:
            self.borrar(clave)


almacenamiento = AlmacenamientoS3()
