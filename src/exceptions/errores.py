"""Rol B: excepciones y registro de incidencias.

Los tipos de excepción y el contrato de reporte están definidos.
El estudiante implementa la estrategia de captura, clasificación y reporte
durante las semanas 11 y 12.
"""
class DataLabError(Exception):
    """Excepción base de la aplicación."""

class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""

class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""

class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""

def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO"):
    # TODO B-S11-01: construir un diccionario de error normalizado.
    # TODO B-S11-02: incluir fecha/hora y categoría sin ocultar el mensaje original.
    # TODO B-S11-03: evitar que el error de un registro interrumpa el lote completo.
    raise NotImplementedError("Pendiente: implementación del rol B, semanas 11–12")
