"""Rol B: excepciones y registro de incidencias.

Los tipos de excepción y el contrato de reporte están definidos.
El estudiante implementa la estrategia de captura, clasificación y reporte
durante las semanas 11 y 12.

REVISIÓN (semanas 11–12): este módulo estaba sin implementar
(NotImplementedError). Se completó para que el procesamiento funcione.
Ideas clave para estudiar:

1. JERARQUÍA DE EXCEPCIONES: todas heredan de DataLabError. Con un solo
   `except DataLabError` se capturan todos los errores PREVISTOS del proyecto,
   y `except Exception` queda como red de seguridad para lo imprevisto.
2. CADA EXCEPCIÓN SABE SU CATEGORÍA: el atributo de clase CATEGORIA evita
   cadenas de if/elif del tipo «si es X, la categoría es Y». Las subclases
   heredan el atributo o lo redefinen.
3. DATO DE MALA CALIDAD ≠ FALLA TÉCNICA: un valor "N/A" es un problema de
   calidad (Rol A, va a registros_invalidos con motivos). Un timeout del
   sensor o una fila CSV rota es una falla técnica (Rol B, va a errores).
"""
from datetime import datetime, timezone


class DataLabError(Exception):
    """Excepción base de la aplicación."""
    # REVISIÓN: categoría por defecto; las subclases la redefinen.
    CATEGORIA = "PROCESAMIENTO"


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""
    CATEGORIA = "VALIDACION"


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""
    CATEGORIA = "FORMATO_FUENTE"


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""
    CATEGORIA = "LECTURA_FUENTE"


# REVISIÓN (B-3, semana 12): excepciones nuevas para los problemas que traen
# los datasets. Heredan de las clases anteriores para conservar la jerarquía.

class ErrorConversion(DataLabError):
    """REVISIÓN: el valor validado no pudo convertirse a número."""
    CATEGORIA = "CONVERSION"


class ErrorEstructuraRegistro(ErrorFormatoFuente):
    """REVISIÓN: UN registro tiene estructura incorrecta.

    Ejemplos: no es un diccionario, es None, o el lector lo marcó con
    `_error_tecnico` (fila CSV con columnas de más o de menos). Es un
    ErrorFormatoFuente que afecta a un solo registro, no a todo el archivo.
    """
    CATEGORIA = "ESTRUCTURA_REGISTRO"


class ErrorEventoSensor(DataLabError):
    """REVISIÓN: el sensor reportó un evento técnico (columna observacion_tecnica)."""
    CATEGORIA = "EVENTO_SENSOR"


class ErrorTimeoutSensor(ErrorEventoSensor):
    """REVISIÓN: el sensor no respondió a tiempo."""
    CATEGORIA = "TIMEOUT_SENSOR"


class ErrorPaqueteIncompleto(ErrorEventoSensor):
    """REVISIÓN: el paquete de datos llegó incompleto."""
    CATEGORIA = "PAQUETE_INCOMPLETO"


class ErrorLecturaIntermitente(ErrorEventoSensor):
    """REVISIÓN: la lectura del sensor fue intermitente (no confiable)."""
    CATEGORIA = "LECTURA_INTERMITENTE"


# REVISIÓN (B-3): tabla que relaciona cada evento simulado con su excepción.
# Para soportar un evento nuevo basta con agregar una línea: el ciclo de
# procesamiento no cambia. Un evento SIMULACION_* que no esté en la tabla
# usa la clase general ErrorEventoSensor.
EVENTOS_TECNICOS = {
    "SIMULACION_TIMEOUT_SENSOR": ErrorTimeoutSensor,
    "SIMULACION_PAQUETE_INCOMPLETO": ErrorPaqueteIncompleto,
    "SIMULACION_LECTURA_INTERMITENTE": ErrorLecturaIntermitente,
}


def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO"):
    # TODO B-S11-01: construir un diccionario de error normalizado.
    # TODO B-S11-02: incluir fecha/hora y categoría sin ocultar el mensaje original.
    # TODO B-S11-03: evitar que el error de un registro interrumpa el lote completo.
    """REVISIÓN (B-2): devuelve un diccionario de error normalizado.

    Las claves coinciden con las que muestra la pestaña «Errores técnicos»:
    identificador, categoria, origen, mensaje, fecha_hora.

    - `mensaje` puede ser texto o una excepción: str(excepcion) conserva el
      mensaje original (TODO B-S11-02: «sin ocultar el mensaje original»).
    - `fecha_hora` en UTC y sin microsegundos (timespec="seconds"), legible en
      la tabla y en el CSV que se descarga.
    - Esta función NUNCA lanza excepciones: si fallara, el error de un registro
      sí podría interrumpir el lote (TODO B-S11-03). Por eso convierte todo a str.
    """
    return {
        "identificador": "N/A" if identificador in (None, "") else str(identificador),
        "categoria": str(categoria),
        "origen": "N/A" if origen in (None, "") else str(origen),
        "mensaje": str(mensaje),
        "fecha_hora": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
