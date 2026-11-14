"""Rol C: selección y unificación de fuentes.

REVISIÓN (semana 12): se conservó la idea original (memoria o lector según
la extensión) y se corrigieron tres detalles marcados con «# REVISIÓN».
"""
from pathlib import Path

from src.data.fuentes_memoria import cargar_desde_memoria
from src.data.lectores import leer_csv, leer_json, leer_excel
# REVISIÓN (C-5): se usan las excepciones del contrato, no ValueError.
from src.exceptions.errores import ErrorFormatoFuente

# REVISIÓN (C-5): tabla extensión → función lectora.
# Las funciones son objetos: se pueden guardar en un diccionario y llamar
# después. Para soportar un formato nuevo basta con agregar una línea.
# Se quitó ".xls": el proyecto instala openpyxl, que solo lee .xlsx;
# aceptar .xls prometía algo que después fallaba.
LECTORES_POR_EXTENSION = {
    "csv": leer_csv,
    "json": leer_json,
    "xlsx": leer_excel,
}


def cargar_datos(archivo=None, nombre_archivo=""):
    """Carga memoria o delega al lector según extensión."""
    if archivo is None:
        return cargar_desde_memoria()

    # REVISIÓN (C-5): si no se envía el nombre, se toma del archivo
    # (atributo .name de Streamlit) o de la ruta.
    if not nombre_archivo:
        nombre_archivo = getattr(archivo, "name", None) or str(archivo)

    # Path(...).suffix devuelve ".csv"; [1:] quita el punto.
    # Si no hay extensión, suffix es "" y el mensaje lo indica.
    extension = Path(str(nombre_archivo)).suffix.lower()[1:]
    lector = LECTORES_POR_EXTENSION.get(extension)
    if lector is None:
        raise ErrorFormatoFuente(
            f"Extensión no soportada: '{extension or 'sin extensión'}'. "
            f"Se aceptan: {', '.join(LECTORES_POR_EXTENSION)}."
        )
    return lector(archivo)
