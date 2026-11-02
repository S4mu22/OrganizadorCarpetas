"""
Módulo: Organizador automático de archivos por extensión.
Descripción: Estructura base del programa.
"""

import os
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

def obtener_extension(nombre_archivo: str) -> str:
    """Obtiene la extensión de un archivo en minúsculas y sin el punto."""
    _, ext = os.path.splitext(nombre_archivo)
    if not ext:
        return "sin_extension"
    return ext.lower().lstrip(".")


def tamano_legible(tamano_bytes: int) -> str:
    """Convierte un tamaño en bytes a bytes, KB, MB o GB dividiendo manualmente."""
    unidades = ["bytes", "KB", "MB", "GB"]
    valor = float(tamano_bytes)
    idx = 0
    while valor >= 1024 and idx < len(unidades) - 1:
        valor /= 1024.0
        idx += 1

    if idx == 0:
        return f"{int(valor)} {unidades[idx]}"
    else:
        return f"{valor:.2f} {unidades[idx]}"


def una_dentro_de_otra(ruta_a: str, ruta_b: str) -> bool:
    """Compara si dos rutas absolutas son la misma o si una está dentro de la otra."""
    abs_a = os.path.abspath(ruta_a) + os.sep
    abs_b = os.path.abspath(ruta_b) + os.sep
    return abs_a.startswith(abs_b) or abs_b.startswith(abs_a)


def nombre_disponible(ruta_destino: str, nombre_archivo: str) -> str:
    """Busca un nombre disponible evitando sobrescribir archivos existentes."""
    ruta_completa = os.path.join(ruta_destino, nombre_archivo)
    if not os.path.exists(ruta_completa):
        return nombre_archivo

    nombre, ext = os.path.splitext(nombre_archivo)
    contador = 1
    while True:
        nuevo_nombre = f"{nombre}_{contador}{ext}"
        ruta_completa = os.path.join(ruta_destino, nuevo_nombre)
        if not os.path.exists(ruta_completa):
            return nuevo_nombre
        contador += 1
def clasificar_archivo(ruta_origen: str, nombre_archivo: str, ruta_destino: str, historial: list) -> int:
    """Mueve un archivo a su subcarpeta de extensión, actualiza el historial (por referencia) y devuelve el tamaño."""
    archivo_origen = os.path.join(ruta_origen, nombre_archivo)
    tamano = os.path.getsize(archivo_origen)

    ext = obtener_extension(nombre_archivo)
    subcarpeta_destino = os.path.join(ruta_destino, ext)
    os.makedirs(subcarpeta_destino, exist_ok=True)

    nombre_final = nombre_disponible(subcarpeta_destino, nombre_archivo)
    archivo_destino = os.path.join(subcarpeta_destino, nombre_final)

    shutil.move(archivo_origen, archivo_destino)

    ruta_rel_origen = os.path.join(ruta_origen, nombre_archivo).replace("\\", "/")
    ruta_rel_destino = os.path.join(ext, nombre_final).replace("\\", "/")
    historial.append(f"{ruta_rel_origen} -> {ruta_rel_destino}")

    return tamano


def clasificar_carpeta_recursivo(ruta_origen: str, ruta_destino: str, historial: list) -> int:
    """Recorre recursivamente carpetas y subcarpetas para clasificar archivos."""
    total_bytes = 0
    try:
        elementos = os.listdir(ruta_origen)
    except PermissionError:
        return 0

    for elemento in elementos:
        ruta_elemento = os.path.join(ruta_origen, elemento)

        # Caso recursivo
        if os.path.isdir(ruta_elemento):
            total_bytes += clasificar_carpeta_recursivo(ruta_elemento, ruta_destino, historial)
        # Caso base / acción directa
        elif os.path.isfile(ruta_elemento):
            bytes_movidos = clasificar_archivo(ruta_origen, elemento, ruta_destino, historial)
            total_bytes += bytes_movidos

    return total_bytes


def contar_archivos_recursivo(ruta: str) -> int:
    """Recorre de forma recursiva una carpeta y cuenta el total de archivos."""
    if not os.path.exists(ruta) or not os.path.isdir(ruta):
        return 0

    total = 0
    try:
        elementos = os.listdir(ruta)
    except PermissionError:
        return 0

    for elemento in elementos:
        ruta_elemento = os.path.join(ruta, elemento)
        if os.path.isdir(ruta_elemento):
            total += contar_archivos_recursivo(ruta_elemento)
        elif os.path.isfile(ruta_elemento):
            total += 1
    return total