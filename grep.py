# Autor: Víctor Adrián García Galván
# Fecha: 21 de mayo de 2026
# Proyecto: Demostración de Paradigma - Motor de búsqueda para archivos de logs

import os
import re
import sys
import time
import queue
import threading

NUM_TRABAJADORES = 3
DIRECTORIO_BASE = "./logs"

PATRONES_PREDEFINIDOS = {
    "errores": r"ERROR.*",
    "advertencias": r"WARNING.*",
    "ips": r"\d+\.\d+\.\d+\.\d+",
    "timeouts": r".*timeout.*",
    "seguridad": r"(SQL injection|Brute force|Unauthorized)",
    "correos": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
}


class ContextoBusqueda:
    def __init__(self):
        self.resultados = []
        self.estadisticas = {
            "archivos_procesados": 0,
            "coincidencias_encontradas": 0,
        }
        self._bloqueo = threading.Lock()

    def agregar_resultado(self, resultado):
        with self._bloqueo:
            self.resultados.append(resultado)
            self.estadisticas["coincidencias_encontradas"] += 1

    def registrar_archivo_procesado(self):
        with self._bloqueo:
            self.estadisticas["archivos_procesados"] += 1


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


def procesar_archivo(ruta_archivo, regex, id_trabajador, contexto):
    try:
        with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                if regex.search(linea):
                    resultado = f"{ruta_archivo}:{numero_linea} {linea.strip()}"
                    contexto.agregar_resultado(resultado)
        contexto.registrar_archivo_procesado()
    except Exception as e:
        print(f"No se pudo leer {ruta_archivo}: {e}")


def trabajador(id_trabajador, regex, cola, contexto):
    while True:
        try:
            ruta_archivo = cola.get(timeout=1)
        except queue.Empty:
            break
        procesar_archivo(ruta_archivo, regex, id_trabajador, contexto)
        cola.task_done()


def principal():
    print("\nGrep Concurrente\n" + "-" * 30)

    if len(sys.argv) < 2:
        print("Uso: python grep.py <patrón> [directorio]")
        print("\nPatrones disponibles: errores, advertencias, ips, timeouts, seguridad, correos")
        print('Ejemplo: python grep.py errores')
        return

    entrada_usuario = sys.argv[1]
    directorio = sys.argv[2] if len(sys.argv) >= 3 else DIRECTORIO_BASE

    patron = resolver_patron(entrada_usuario)
    print(f"regex: {patron}")
    print(f"carpeta: {directorio}")

    try:
        regex = re.compile(patron, re.IGNORECASE)
    except re.error as e:
        print(f"\nRegex inválida: {e}")
        return

    archivos = escanear_archivos(directorio)
    if not archivos:
        print("\nNo se encontraron archivos")
        return

    print(f"archivos: {len(archivos)}\n")

    cola = queue.Queue()
    for archivo in archivos:
        cola.put(archivo)

    contexto = ContextoBusqueda()

    tiempo_inicio = time.time()
    hilos = [threading.Thread(target=trabajador, args=(i + 1, regex, cola, contexto)) for i in range(NUM_TRABAJADORES)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    tiempo_fin = time.time()

    print("-" * 30)
    if contexto.resultados:
        for resultado in contexto.resultados:
            print(resultado)
    else:
        print("Sin coincidencias")

    print("-" * 30)
    print(f"procesados: {contexto.estadisticas['archivos_procesados']} archivos")
    print(f"coincidencias: {contexto.estadisticas['coincidencias_encontradas']}")
    print(f"tiempo: {tiempo_fin - tiempo_inicio:.4f}s\n")


if __name__ == "__main__":
    principal()