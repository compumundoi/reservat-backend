import os
from pathlib import Path

def update_cors_origins():
    base_dir = Path("/Users/deiverjc/Code/reservat/reservat-backend")
    
    # Buscar todos los archivos app.py en los microservicios
    app_files = list(base_dir.glob("ms_*/src/app.py"))
    
    print(f"🔍 Encontrados {len(app_files)} archivos app.py")
    
    for app_file in app_files:
        try:
            content = app_file.read_text()
            
            # Verificar si ya tiene el puerto 3002
            if '"http://localhost:3002"' in content or "'http://localhost:3002'" in content:
                print(f"✅ {app_file.parent.parent.name} ya tiene el puerto 3002 configurado.")
                continue
                
            # Buscar la línea del puerto 3000 o 3001 y añadir el 3002
            if '"http://localhost:3001"' in content:
                new_content = content.replace(
                    '"http://localhost:3001",',
                    '"http://localhost:3001",\n    "http://localhost:3002",'
                )
            elif "'http://localhost:3001'" in content:
                new_content = content.replace(
                    "'http://localhost:3001',",
                    "'http://localhost:3001',\n    'http://localhost:3002',"
                )
            elif '"http://localhost:3000"' in content:
                new_content = content.replace(
                    '"http://localhost:3000",',
                    '"http://localhost:3000",\n    "http://localhost:3001",\n    "http://localhost:3002",'
                )
            elif "'http://localhost:3000'" in content:
                new_content = content.replace(
                    "'http://localhost:3000',",
                    "'http://localhost:3000',\n    'http://localhost:3001',\n    'http://localhost:3002',"
                )
            else:
                print(f"⚠️ No se encontró una entrada compatible en {app_file}")
                continue
                
            app_file.write_text(new_content)
            print(f"✨ Actualizado {app_file.parent.parent.name}")
            
        except Exception as e:
            print(f"❌ Error procesando {app_file}: {e}")

if __name__ == "__main__":
    update_cors_origins()
