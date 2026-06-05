# Autor: Víctor Adrián García Galván
# Fecha: 21 de mayo de 2026
# Genera archivos de log sintéticos para pruebas de benchmark

import os
import random

DIRECTORIO_SALIDA   = "./logs_benchmark"
NUM_ARCHIVOS        = 800
LINEAS_POR_ARCHIVO  = 300

LINEAS_MUESTRA = [
    "INFO Iniciando servicio en 192.168.1.10",
    "ERROR Tiempo de espera agotado al conectar con la base de datos",
    "WARNING Espacio en disco bajo: 15% disponible",
    "INFO Conexión aceptada desde 10.0.0.23",
    "ERROR Intento de SQL injection detectado desde 203.0.113.7",
    "INFO Configuración cargada correctamente",
    "ERROR Fallo de autenticación para el usuario admin@empresa.com",
    "WARNING Certificado SSL próximo a vencer",
    "INFO Tarea programada ejecutada con éxito",
    "ERROR Brute force detectado: 50 intentos fallidos en 10s",
]

os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)

for i in range(NUM_ARCHIVOS):
    ruta = os.path.join(DIRECTORIO_SALIDA, f"log_{i:04d}.txt")
    with open(ruta, "w", encoding="utf-8") as archivo:
        for _ in range(LINEAS_POR_ARCHIVO):
            archivo.write(random.choice(LINEAS_MUESTRA) + "\n")

print(f"Generados {NUM_ARCHIVOS} archivos en '{DIRECTORIO_SALIDA}'")