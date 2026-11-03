"""Fachada entre Streamlit y la lógica de DataLab.

Este módulo es provisto por el docente. No debe ser modificado por los estudiantes.
La interfaz se ejecuta desde el día uno con el modo de demostración en memoria.
"""
from src.data.fuentes_memoria import cargar_desde_memoria
from src.processing.procesamiento import procesar_registros
from src.processing.resumen import generar_resumen

def obtener_datos_demo():
    return cargar_desde_memoria()

def ejecutar_demo():
    registros = obtener_datos_demo()
    resultado = procesar_registros(registros)
    return resultado, generar_resumen(resultado["registros_validos"])
