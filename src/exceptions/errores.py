"""Rol B: excepciones y registro de incidencias.

REVISIÓN (semanas 11-12):
  - Cada excepción tiene ahora un atributo de clase CATEGORIA. Así el
    procesamiento no necesita una cadena de if/elif para saber la categoría:
    basta con leer error.CATEGORIA (las subclases la heredan o la cambian).
  - Se agregan ErrorConversion, ErrorEstructuraRegistro y la familia
    ErrorEventoSensor (timeout, paquete incompleto, lectura intermitente),
    que los datasets, la interfaz y las pruebas del docente esperan.
  - El reporte usa la clave "fecha_hora" (contrato de la interfaz docente),
    no "timestamp".
"""
from datetime import datetime, timezone


class DataLabError(Exception):
    """Excepción base de la aplicación."""
    CATEGORIA = "DATALAB"


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""
    CATEGORIA = "VALIDACION"


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado
    (extensión no soportada, columnas faltantes, JSON que no es una lista...)."""
    CATEGORIA = "FORMATO"


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos (archivo dañado, codificación...)."""
    CATEGORIA = "LECTURA"


# --- REVISIÓN: excepciones nuevas -------------------------------------------

class ErrorConversion(DataLabError):
    """Un valor que pasó la validación no se pudo convertir a número (semana 12)."""
    CATEGORIA = "CONVERSION"


class ErrorEstructuraRegistro(ErrorFormatoFuente):
    """Un registro individual llegó roto: no es diccionario o el lector lo
    marcó con la clave "_error_tecnico" (por ejemplo, una fila irregular del CSV).
    Hereda de ErrorFormatoFuente porque es un problema de estructura."""
    CATEGORIA = "ESTRUCTURA_REGISTRO"


class ErrorEventoSensor(DataLabError):
    """Falla técnica reportada por el propio sensor en la columna
    "observacion_tecnica" (valores que empiezan con "SIMULACION_")."""
    CATEGORIA = "EVENTO_SENSOR"


class ErrorTimeoutSensor(ErrorEventoSensor):
    """El sensor no respondió a tiempo (SIMULACION_TIMEOUT_SENSOR)."""
    CATEGORIA = "TIMEOUT_SENSOR"


class ErrorPaqueteIncompleto(ErrorEventoSensor):
    """El paquete de datos llegó incompleto (SIMULACION_PAQUETE_INCOMPLETO)."""
    CATEGORIA = "PAQUETE_INCOMPLETO"


class ErrorLecturaIntermitente(ErrorEventoSensor):
    """La lectura del sensor fue intermitente (SIMULACION_LECTURA_INTERMITENTE)."""
    CATEGORIA = "LECTURA_INTERMITENTE"


# Tabla evento -> excepción. Agregar un evento nuevo = agregar una línea aquí,
# sin tocar procesamiento.py. Un "SIMULACION_..." que no esté en la tabla se
# reporta con la clase general ErrorEventoSensor.
EVENTOS_TECNICOS = {
    "SIMULACION_TIMEOUT_SENSOR": ErrorTimeoutSensor,
    "SIMULACION_PAQUETE_INCOMPLETO": ErrorPaqueteIncompleto,
    "SIMULACION_LECTURA_INTERMITENTE": ErrorLecturaIntermitente,
}


def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO"):
    """Crea un diccionario normalizado con los datos del error.

    Claves (contrato con la interfaz docente, pestaña "Errores técnicos"):
    identificador, categoria, origen, mensaje, fecha_hora.

    REVISIÓN (B-2, 18-nov): el cambio local más reciente quitó dos detalles
    que se restauran:
      - El README pide «fecha/hora UTC». `datetime.now()` da la hora LOCAL
        del equipo: dos equipos en zonas distintas darían horas distintas
        para el mismo instante. `datetime.now(timezone.utc)` es inequívoca.
      - Un registro `None` o sin id llegaba con identificador None. Se
        reemplaza por "N/A" y todo se convierte a str: esta función NUNCA
        debe lanzar una excepción, porque se llama DENTRO del `except` del
        procesamiento; si fallara ahí, el error de un registro sí detendría
        el lote (TODO B-S11-03).
    """
    return {
        "fecha_hora": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "origen": "N/A" if origen in (None, "") else str(origen),
        "identificador": "N/A" if identificador in (None, "") else str(identificador),
        "categoria": str(categoria),
        "mensaje": str(mensaje),
    }
