# Autor: Víctor Adrián García Galván
# Fecha: 21 de mayo de 2026
# Proyecto: Demostración de Paradigma

import os
import re
import sys
import time
import queue
import threading

NUM_WORKERS = 4
DIRECTORIO = "./logs"

PATRONES_PREDEFINIDOS = {
    "errores": r"ERROR.*",
    "advertencias": r"WARNING.*",
    "ips": r"\d+\.\d+\.\d+\.\d+",
    "timeouts": r".*timeout.*",
    "seguridad": r"(SQL injection|Brute force|Unauthorized)",
    "correos": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
}

cola_archivos = queue.Queue()
resultados = []
bloqueo_resultados = threading.Lock()

estadisticas = {
    "archivos_procesados": 0,
    "coincidencias_encontradas": 0
}


def resolver_patron(entrada_usuario):
    if entrada_usuario.lower() in PATRONES_PREDEFINIDOS:
        patron = PATRONES_PREDEFINIDOS[entrada_usuario.lower()]
        print(f"patrón: {entrada_usuario} (predefinido)")
    else:
        patron = rf".*{re.escape(entrada_usuario)}.*"
        print(f"patrón: '{entrada_usuario}' ")
    return patron


def escanear_archivos(directorio):
    archivos = []
    for raiz, dirs, nombres_archivos in os.walk(directorio):
        for nombre_archivo in nombres_archivos:
            archivos.append(os.path.join(raiz, nombre_archivo))
    return archivos


def procesar_archivo(ruta_archivo, regex, id_worker):
    try:
        with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                if regex.search(linea):
                    resultado = f"{ruta_archivo}:{numero_linea} {linea.strip()}"
                    with bloqueo_resultados:
                        resultados.append(resultado)
                        estadisticas["coincidencias_encontradas"] += 1
        with bloqueo_resultados:
            estadisticas["archivos_procesados"] += 1
    except Exception as e:
        print(f"No se pudo leer {ruta_archivo}: {e}")


def worker(id_worker, regex):
    while True:
        try:
            ruta_archivo = cola_archivos.get(timeout=1)
        except queue.Empty:
            break
        procesar_archivo(ruta_archivo, regex, id_worker)
        cola_archivos.task_done()


def principal():
    print("\nGrep Concurrente\n" + "-" * 30)

    if len(sys.argv) < 2:
        print("Uso: python grep.py <patrón> [directorio]")
        print("\nPatrones disponibles: errores, advertencias, ips, timeouts, seguridad, correos")
        print('Ejemplo: python grep.py errores')
        return

    entrada_usuario = sys.argv[1]
    directorio = sys.argv[2] if len(sys.argv) >= 3 else DIRECTORIO

    patron = resolver_patron(entrada_usuario)
    print(f"regex: {patron}")
    print(f"carpeta: {directorio}")

    try:
        regex = re.compile(patron, re.IGNORECASE)
    except re.error as e:
        print(f"\n Regex inválida: {e}")
        return

    archivos = escanear_archivos(directorio)
    if not archivos:
        print("\n No se encontraron archivos")
        return

    print(f"  archivos: {len(archivos)}\n")

    for archivo in archivos:
        cola_archivos.put(archivo)

    tiempo_inicio = time.time()

    hilos = [threading.Thread(target=worker, args=(i + 1, regex)) for i in range(NUM_WORKERS)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    tiempo_fin = time.time()

    # Resultados
    print("-" * 30)
    if resultados:
        for resultado in resultados:
            print(resultado)
    else:
        print("Sin coincidencias")

    # Estadísticas
    print("-" * 30)
    print(f"procesados: {estadisticas['archivos_procesados']} archivos")
    print(f"coincidencias: {estadisticas['coincidencias_encontradas']}")
    print(f"tiempo: {tiempo_fin - tiempo_inicio:.4f}s\n")


if __name__ == "__main__":
    principal()
