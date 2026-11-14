"""Rol C: lectores de archivos. Implementación del estudiante en semana 12.

Contrato de salida para cada lector: list[dict] con claves id, tipo, valor, unidad.
Los lectores no normalizan ni clasifican: entregan datos crudos al servicio.

REVISIÓN (semana 12): los tres lectores estaban sin implementar
(NotImplementedError). Ideas clave para estudiar:

1. (C-1) PATRÓN ADAPTADOR: `_obtener_bytes` convierte cualquier entrada (ruta,
   bytes, archivo de Streamlit, archivo abierto) a bytes. Así los tres
   lectores trabajan siempre sobre el mismo tipo de dato.
2. (C-6) SALIDA HOMOGÉNEA: CSV, JSON y Excel devuelven list[dict] con las mismas
   claves, más dos metadatos de trazabilidad: `_origen` (nombre del archivo)
   y `_fila` (posición en el archivo). Streamlit los muestra como
   «origen» y «fila».
3. (C-4) DOS NIVELES DE FALLA:
   - Falla de TODO el archivo (no existe, no es UTF-8, JSON mal formado,
     faltan columnas): se lanza ErrorLecturaFuente o ErrorFormatoFuente,
     porque no es posible procesar sus filas de forma confiable.
   - Falla de UNA fila (columnas de más o de menos): la fila se MARCA con
     `_error_tecnico` y la lectura continúa. El Rol B la reporta como error
     técnico. Una fila rota no debe impedir leer las otras 622.
"""
# REVISIÓN: PEP 8 — todas las importaciones al inicio del archivo, agrupadas:
# biblioteca estándar, terceros y módulos del proyecto.
import csv
import io
import json
from pathlib import Path

import pandas as pd

from src.exceptions.errores import ErrorFormatoFuente, ErrorLecturaFuente

# REVISIÓN: columnas mínimas del registro canónico (docs/contratos_modulos.md).
COLUMNAS_OBLIGATORIAS = ("id", "tipo", "valor", "unidad")


# --------------------------------------------------------------------------
# Funciones auxiliares (el guion bajo indica «uso interno del módulo»)
# --------------------------------------------------------------------------
def _nombre_origen(archivo):
    """REVISIÓN: nombre del archivo para la trazabilidad (`_origen`)."""
    if isinstance(archivo, (str, Path)):
        return Path(archivo).name
    nombre = getattr(archivo, "name", None)  # UploadedFile de Streamlit
    return Path(nombre).name if nombre else "memoria"


def _obtener_bytes(archivo):
    """REVISIÓN (C-1): adaptador que convierte cualquier entrada a bytes.

    Streamlit entrega un objeto UploadedFile (parecido a un archivo), no una
    ruta: `open(archivo)` fallaría con TypeError. Con `hasattr` se acepta
    «cualquier cosa que tenga .getvalue() o .read()» sin conocer su clase
    (duck typing).
    """
    if isinstance(archivo, (str, Path)):
        try:
            return Path(archivo).read_bytes()
        except OSError as exc:  # incluye FileNotFoundError y PermissionError
            raise ErrorLecturaFuente(f"No fue posible abrir {archivo}: {exc}") from exc
    if isinstance(archivo, (bytes, bytearray)):
        return bytes(archivo)
    if hasattr(archivo, "getvalue"):   # Streamlit UploadedFile, io.BytesIO
        contenido = archivo.getvalue()
    elif hasattr(archivo, "read"):     # archivo abierto con open(...)
        contenido = archivo.read()
    else:
        raise ErrorFormatoFuente(
            f"Tipo de archivo no soportado: {type(archivo).__name__}."
        )
    # io.StringIO o un archivo abierto en modo texto entregan str: se codifica.
    return contenido.encode("utf-8") if isinstance(contenido, str) else contenido


def _obtener_texto(archivo):
    """REVISIÓN: bytes → texto. `utf-8-sig` elimina el BOM que agrega Excel
    al guardar CSV (el primer encabezado sería «\\ufeffid» en lugar de «id»)."""
    try:
        return _obtener_bytes(archivo).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ErrorLecturaFuente(
            f"{_nombre_origen(archivo)} no está codificado en UTF-8: {exc}"
        ) from exc


def _verificar_columnas(columnas, origen):
    """REVISIÓN: lanza ErrorFormatoFuente si faltan columnas obligatorias."""
    faltantes = [c for c in COLUMNAS_OBLIGATORIAS if c not in columnas]
    if faltantes:
        raise ErrorFormatoFuente(
            f"{origen}: faltan las columnas obligatorias {', '.join(faltantes)}."
        )


# --------------------------------------------------------------------------
# Lectores públicos (contrato del Rol C)
# --------------------------------------------------------------------------
def leer_csv(archivo):
    # TODO C-S12-01: leer CSV y devolver lista de diccionarios.
    """REVISIÓN: lee un CSV y devuelve list[dict] con `_origen` y `_fila`."""
    origen = _nombre_origen(archivo)
    # csv.reader (no DictReader) permite detectar filas con columnas de más
    # o de menos: DictReader las ocultaría con una clave None o valores None.
    filas = csv.reader(io.StringIO(_obtener_texto(archivo)))

    encabezado = next(filas, None)
    if not encabezado:
        raise ErrorFormatoFuente(f"{origen}: el archivo CSV está vacío.")
    encabezado = [columna.strip() for columna in encabezado]
    _verificar_columnas(encabezado, origen)

    registros = []
    # enumerate(..., start=2): la fila 1 es el encabezado.
    for numero_fila, fila in enumerate(filas, start=2):
        if not any(celda.strip() for celda in fila):
            continue  # se ignoran las líneas en blanco
        if len(fila) != len(encabezado):
            # REVISIÓN (C-4): falla de UNA fila; se marca y se sigue leyendo.
            registros.append({
                "id": fila[0] if fila else None,
                "_error_tecnico": (
                    f"Fila irregular: tiene {len(fila)} columnas y se "
                    f"esperaban {len(encabezado)}."
                ),
                "_origen": origen,
                "_fila": numero_fila,
            })
            continue
        registro = dict(zip(encabezado, fila))
        registro["_origen"] = origen
        registro["_fila"] = numero_fila
        registros.append(registro)
    return registros


def leer_json(archivo):
    # TODO C-S12-02: leer JSON y devolver lista de diccionarios.
    """REVISIÓN: lee un JSON con una lista de registros.

    Acepta dos formas: `[ {...}, {...} ]` o `{"registros": [ {...} ]}`
    (presion.json usa la segunda).
    """
    origen = _nombre_origen(archivo)
    try:
        datos = json.loads(_obtener_texto(archivo))
    except json.JSONDecodeError as exc:
        raise ErrorLecturaFuente(
            f"{origen}: JSON mal formado en la línea {exc.lineno}, "
            f"columna {exc.colno} ({exc.msg})."
        ) from exc

    if isinstance(datos, dict) and isinstance(datos.get("registros"), list):
        datos = datos["registros"]
    if not isinstance(datos, list):
        raise ErrorFormatoFuente(
            f"{origen}: se esperaba una lista de registros o "
            f"{{\"registros\": [...]}} y se recibió {type(datos).__name__}."
        )

    registros = []
    for posicion, elemento in enumerate(datos, start=1):
        if isinstance(elemento, dict):
            # Se copia para no modificar los datos leídos.
            registro = dict(elemento)
        else:
            # Un elemento que no es objeto JSON se marca, no detiene la lectura.
            registro = {"_error_tecnico": (
                f"Elemento JSON no es un objeto: {type(elemento).__name__}."
            )}
        registro["_origen"] = origen
        registro["_fila"] = posicion
        registros.append(registro)
    return registros


def leer_excel(archivo):
    # TODO C-S12-03: leer Excel y devolver lista de diccionarios.
    """REVISIÓN: lee la primera hoja de un Excel (.xlsx) como list[dict]."""
    origen = _nombre_origen(archivo)
    try:
        tabla = pd.read_excel(
            io.BytesIO(_obtener_bytes(archivo)),
            # dtype=object: pandas NO fuerza tipos; cada celda conserva el tipo
            # que tiene en Excel. Convertir y validar es tarea del Rol A y B.
            dtype=object,
        )
    except (ValueError, OSError, KeyError) as exc:
        # Archivo dañado o que no es un Excel válido: falla de todo el archivo.
        raise ErrorLecturaFuente(f"{origen}: no es un archivo Excel válido ({exc}).") from exc

    if tabla.empty and len(tabla.columns) == 0:
        raise ErrorFormatoFuente(f"{origen}: la hoja de Excel está vacía.")
    tabla.columns = [str(columna).strip() for columna in tabla.columns]
    _verificar_columnas(tabla.columns, origen)

    # REVISIÓN (C-6) SALIDA HOMOGÉNEA: pandas representa las celdas vacías como NaN (float).
    # Se cambian por None, igual que un `null` de JSON. Así ningún NaN viaja
    # a los demás módulos. (Nota: pandas también interpreta los textos "N/A",
    # "NA" y "null" como celda vacía; ver la observación general del informe.)
    tabla = tabla.astype(object).where(tabla.notna(), None)

    registros = []
    # La fila 1 de Excel es el encabezado; el índice 0 de pandas es la fila 2.
    for indice, registro in enumerate(tabla.to_dict(orient="records")):
        registro["_origen"] = origen
        registro["_fila"] = indice + 2
        registros.append(registro)
    return registros
