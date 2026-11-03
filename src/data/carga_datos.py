"""Rol C: selección y unificación de fuentes."""
from src.data.fuentes_memoria import cargar_desde_memoria
from src.data.lectores import leer_csv, leer_json, leer_excel

def cargar_datos(archivo=None, nombre_archivo=""):
    """Carga memoria o delega al lector según extensión."""
    if archivo is None:
        return cargar_desde_memoria()
    extension = nombre_archivo.lower().rsplit(".", 1)[-1]
    if extension == "csv":
        return leer_csv(archivo)
    if extension == "json":
        return leer_json(archivo)
    if extension in ("xlsx", "xls"):
        return leer_excel(archivo)
    raise ValueError(f"Extensión no soportada: {extension}")
