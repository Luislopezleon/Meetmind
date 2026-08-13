#!/usr/bin/env python3
"""
Script simple para verificar que la base del proyecto funciona.
"""

import os
import sys

def check_file_structure():
    """Verificar que la estructura de archivos está completa."""
    required_files = [
        "backend/app/main.py",
        "backend/app/models/__init__.py", 
        "backend/app/schemas/__init__.py",
        "backend/app/core/config.py",
        "backend/app/db/database.py",
        "docker-compose.yml",
        "docs/README.md",
        ".env"
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        print("❌ Archivos faltantes:")
        for f in missing:
            print(f"  - {f}")
        return False
    else:
        print("✅ Estructura de archivos completa")
        return True

def check_docker_services():
    """Verificar que los servicios Docker están corriendo."""
    import subprocess
    
    try:
        # Verificar PostgreSQL
        result = subprocess.run([
            "docker", "exec", "project-db-1", 
            "psql", "-U", "meetmind", "-d", "meetmind", 
            "-c", "SELECT 1;"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL funcionando")
        else:
            print("❌ PostgreSQL no responde")
            return False
            
        # Verificar Redis
        result = subprocess.run([
            "docker", "exec", "project-redis-1", 
            "redis-cli", "ping"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and "PONG" in result.stdout:
            print("✅ Redis funcionando")
        else:
            print("❌ Redis no responde")  
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando servicios: {e}")
        return False

def count_code_lines():
    """Contar líneas de código creadas."""
    import glob
    
    patterns = [
        "backend/app/**/*.py",
        "backend/tests/**/*.py", 
        "docs/*.md"
    ]
    
    total_lines = 0
    total_files = 0
    
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    total_files += 1
            except:
                pass
    
    print(f"📊 Código creado: {total_files} archivos, {total_lines} líneas")
    return total_lines

def main():
    print("🔍 REVISIÓN MeetMind - Task 1")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto
    os.chdir("/home/llopez/Escritorio/project")
    
    checks = [
        check_file_structure(),
        check_docker_services()
    ]
    
    count_code_lines()
    
    if all(checks):
        print("\n🎉 TASK 1 - REVISIÓN EXITOSA")
        print("La base del proyecto está sólida y funcionando.")
        print("Listo para continuar con Task 2 (Recall.ai integration)")
    else:
        print("\n⚠️  Hay algunos problemas que resolver antes de continuar.")
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)