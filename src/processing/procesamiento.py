"""Orquestación del procesamiento.

Semana 10–12: completar integración con validación y excepciones.
La clasificación permanece centralizada en clasificacion.py.

REVISIÓN (semanas 10–12): este módulo estaba sin implementar
(NotImplementedError), por eso ni la demostración en memoria de Streamlit
funcionaba. Flujo de cada registro (ver procesar_registros):

    registro crudo
      │  1. ¿estructura rota o evento técnico?  ──► errores            (Rol B)
      │  2. normalizar_registro (copia)                                (Rol A)
      │  3. validar_registro → motivos?         ──► registros_invalidos (Rol A)
      │  4. convertir valor a float             ──► errores si falla    (Rol B)
      │  5. clasificar_valor (centralizada)
      ▼
    registros_validos ──► generar_resumen

Cada registro termina en UNA sola bandeja: válidos + inválidos + errores =
total de registros recibidos. Ninguno se pierde y ninguno se cuenta dos veces.
"""
from src.processing.clasificacion import clasificar_valor
# REVISIÓN: se importan las funciones de los otros módulos en lugar de copiar
# sus reglas. «No duplicar» es una regla del proyecto (TODO B-S10-01).
from src.processing.resumen import generar_resumen
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro
from src.exceptions.errores import (
    DataLabError,
    ErrorConversion,
    ErrorEstructuraRegistro,
    ErrorEventoSensor,
    ErrorFormatoFuente,
    EVENTOS_TECNICOS,
    crear_reporte_error,
)

# REVISIÓN: origen por defecto cuando el registro no trae `_origen`
# (por ejemplo, los registros de la demostración en memoria).
ORIGEN_LOTE = "lote"


def _identificador(registro):
    """REVISIÓN: id del registro para el reporte, sin fallar si no es dict."""
    if isinstance(registro, dict):
        return registro.get("id")
    return None


def _origen(registro):
    """REVISIÓN: origen del registro (archivo y fila si el lector los dejó)."""
    if not isinstance(registro, dict) or "_origen" not in registro:
        return ORIGEN_LOTE
    if "_fila" in registro:
        return f"{registro['_origen']} (fila {registro['_fila']})"
    return str(registro["_origen"])


def _revisar_eventos_tecnicos(registro):
    """REVISIÓN (B-3): lanza una excepción si el registro tiene una falla técnica.

    Se revisa ANTES de normalizar y validar: un registro con timeout no es
    «de mala calidad», es un registro en el que no se puede confiar.
    """
    if not isinstance(registro, dict):
        raise ErrorEstructuraRegistro(
            f"Se esperaba un diccionario y se recibió {type(registro).__name__}."
        )
    # El Rol C marca así una fila que no pudo leer correctamente (C-4).
    if "_error_tecnico" in registro:
        raise ErrorEstructuraRegistro(str(registro["_error_tecnico"]))

    evento = registro.get("observacion_tecnica")
    if isinstance(evento, str) and evento.strip().upper().startswith("SIMULACION_"):
        codigo = evento.strip().upper()
        # .get con valor por defecto: un evento desconocido usa la clase general.
        clase_error = EVENTOS_TECNICOS.get(codigo, ErrorEventoSensor)
        raise clase_error(f"Evento técnico del sensor: {codigo}")


def _convertir_valor(registro):
    """REVISIÓN (B-5): convierte el valor a float o lanza ErrorConversion.

    `raise ... from exc` conserva el error original como causa (__cause__),
    útil para depurar sin ocultar el mensaje original.
    """
    try:
        return float(registro["valor"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ErrorConversion(
            f"No se pudo convertir el valor {registro.get('valor')!r} a número."
        ) from exc


def _resultado_vacio(error=None):
    """REVISIÓN (B-5): contrato común sin registros.

    Se usa generar_resumen([]) en lugar de {} para que quien consume el
    resultado siempre encuentre las mismas claves (total, promedio, ...).
    """
    return {
        "registros_validos": [],
        "registros_invalidos": [],
        "errores": [error] if error else [],
        "resumen": generar_resumen([]),
    }


def procesar_registros(registros):
    # TODO B-S10-01: coordinar normalización y validación sin duplicar reglas.
    # TODO B-S10-02: clasificar únicamente registros válidos.
    # TODO B-S10-03: devolver el contrato común definido en docs/contratos_modulos.md.
    # TODO B-S11-04: aislar errores por registro y continuar el lote.
    # TODO B-S12-04: integrar entradas de lectores CSV, JSON y Excel.
    # La función clasificar_valor(valor, tipo) debe reutilizarse.
    """REVISIÓN: implementación de los TODO B-S10-01 a B-S12-04.

    Devuelve el contrato común:
    {registros_validos, registros_invalidos, errores, resumen}.
    """
    # REVISIÓN: una entrada que no es lista (o tupla) es un error de formato
    # de TODA la fuente; se reporta y se devuelve el contrato vacío.
    if not isinstance(registros, (list, tuple)):
        error = ErrorFormatoFuente(
            f"Se esperaba una lista de registros y se recibió "
            f"{type(registros).__name__}."
        )
        return _resultado_vacio(
            crear_reporte_error(ORIGEN_LOTE, "N/A", error, error.CATEGORIA)
        )

    validos = []
    invalidos = []
    errores = []

    for registro in registros:
        # REVISIÓN (B-S11-04): try/except POR REGISTRO. Si un registro falla,
        # se reporta y el ciclo continúa con el siguiente: el lote no se detiene.
        try:
            # 1. Fallas técnicas (Rol B): evento del sensor o estructura rota.
            _revisar_eventos_tecnicos(registro)

            # 2. Normalización (Rol A): devuelve una copia, no altera el original.
            registro_norm = normalizar_registro(registro)

            # 3. Validación (Rol A): devuelve (es_valido, motivos).
            es_valido, motivos = validar_registro(registro_norm)
            if not es_valido:
                # REVISIÓN (B-1): forma que espera la interfaz:
                # {"registro": ..., "motivos": [...]}. Se separa «lo que dijo
                # el sensor» de «lo que dijo la revisión»; así el registro no
                # se mezcla con campos ajenos.
                invalidos.append({"registro": registro_norm, "motivos": motivos})
                # continue salta a la siguiente iteración (ahorra un else).
                continue

            # 4. Conversión (Rol B): el valor puede llegar como texto "22.5".
            registro_norm["valor"] = _convertir_valor(registro_norm)

            # 5. Clasificación centralizada, SOLO para válidos (B-S10-02).
            registro_norm["clasificacion"] = clasificar_valor(
                registro_norm["valor"], registro_norm["tipo"]
            )
            validos.append(registro_norm)

        # REVISIÓN (B-4): errores PREVISTOS. Cada excepción sabe su categoría
        # (atributo CATEGORIA), así que no hace falta una cadena de if/elif.
        except DataLabError as error:
            errores.append(crear_reporte_error(
                _origen(registro), _identificador(registro), error, error.CATEGORIA
            ))
        # REVISIÓN (B-4): red de seguridad para errores IMPREVISTOS.
        # El orden importa: el except más específico va primero; si
        # `except Exception` fuera primero, capturaría también los DataLabError.
        except Exception as error:
            errores.append(crear_reporte_error(
                _origen(registro), _identificador(registro),
                f"Error inesperado ({type(error).__name__}): {error}", "SISTEMA"
            ))

    return {
        "registros_validos": validos,
        "registros_invalidos": invalidos,
        "errores": errores,
        "resumen": generar_resumen(validos),
    }
