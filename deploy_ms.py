import os
import subprocess
import re
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).parent
DB_HOST = "host.docker.internal"  # Para conectar al PostgreSQL del host desde Docker

def get_exposed_port(dockerfile_path):
    """Extrae el puerto del comando EXPOSE en el Dockerfile"""
    try:
        content = dockerfile_path.read_text()
        match = re.search(r"EXPOSE\s+(\d+)", content)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error leyendo {dockerfile_path}: {e}")
    return None

def run_command(command, cwd=None):
    """Ejecuta un comando en la terminal"""
    print(f"🚀 Ejecutando: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    return result.returncode == 0

def deploy_microservices():
    # Buscar carpetas que empiecen con ms_
    ms_dirs = [d for d in BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("ms_")]
    
    # Ordenar por nombre para consistencia
    ms_dirs.sort(key=lambda x: x.name)

    print(f"🔍 Encontrados {len(ms_dirs)} microservicios.")

    for ms_dir in ms_dirs:
        dockerfile = ms_dir / "Dockerfile"
        if not dockerfile.exists():
            print(f"⚠️  No se encontró Dockerfile en {ms_dir.name}, saltando...")
            continue

        port = get_exposed_port(dockerfile)
        if not port:
            print(f"⚠️  No se pudo determinar el puerto EXPOSE en {ms_dir.name}, saltando...")
            continue

        service_name = ms_dir.name.lower().replace("_", "-")
        image_name = service_name
        container_name = service_name

        print(f"\n--- 🛠️  Procesando {service_name} (Puerto: {port}) ---")

        # 1. Build de la imagen
        print(f"🏗️  Construyendo imagen {image_name}...")
        if not run_command(f"docker build -t {image_name} .", cwd=ms_dir):
            print(f"❌ Error construyendo {image_name}")
            continue

        # 2. Detener y eliminar contenedor antiguo si existe
        print(f"🗑️  Limpiando contenedor antiguo...")
        subprocess.run(f"docker stop {container_name}", shell=True, capture_output=True)
        subprocess.run(f"docker rm {container_name}", shell=True, capture_output=True)

        # 3. Ejecutar nuevo contenedor
        # Se incluye DB_HOST=host.docker.internal para que usen el PostgreSQL del host
        print(f"🚀 Iniciando contenedor {container_name}...")
        run_cmd = (
            f"docker run -d "
            f"--name {container_name} "
            f"-p {port}:{port} "
            f"-e DB_HOST={DB_HOST} "
            f"{image_name}"
        )
        
        if run_command(run_cmd):
            print(f"✅ {service_name} desplegado con éxito en el puerto {port}")
        else:
            print(f"❌ Error iniciando el contenedor {container_name}")

if __name__ == "__main__":
    deploy_microservices()
    print("\n✅ Proceso de despliegue finalizado.")
