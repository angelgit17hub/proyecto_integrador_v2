"""Fachada entre Streamlit y la lógica de DataLab."""
from src.data.carga_datos import cargar_datos
from src.processing.procesamiento import procesar_registros


def obtener_datos_demo():
    return cargar_datos()


def ejecutar_demo():
    return procesar_registros(obtener_datos_demo())


def ejecutar_archivo(archivo, nombre_archivo):
    registros=cargar_datos(archivo, nombre_archivo)
    return procesar_registros(registros)
