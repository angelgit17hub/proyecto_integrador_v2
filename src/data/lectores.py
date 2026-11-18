"""Rol C: lectores de archivos CSV, JSON y Excel (semana 12).

Contrato de salida de TODOS los lectores (docs/contratos_modulos.md):
    list[dict] con las claves id, tipo, valor, unidad (más las columnas que
    traiga el archivo, como fecha y observacion_tecnica) y dos metadatos de
    trazabilidad: `_origen` (nombre del archivo) y `_fila` (posición).
Los lectores NO normalizan, NO validan y NO clasifican: entregan los datos
tal como vienen. Esas tareas son del Rol A y del Rol B.

REVISIÓN (semana 12, segunda entrega del Rol C — commit 75ebe15):
Los estudiantes propusieron un diseño orientado a objetos (clase abstracta
`LectorBase` y una subclase por formato). La idea es buena y SE CONSERVA.
Pero la versión entregada rompía la aplicación y perdía funciones que los
demás módulos usan. Correcciones (ver revision/revision_semanas_10_12.html):

  C-7  La clase solo aceptaba rutas: Streamlit entrega un `UploadedFile`, no
       una ruta, y `os.path.exists(UploadedFile)` lanza TypeError.
       → `_obtener_bytes` (patrón adaptador) acepta ruta, bytes o archivo.
  C-8  Se perdieron `_origen` y `_fila`, la marca `_error_tecnico` de filas
       irregulares, el formato {"registros": [...]} de presion.json, el BOM
       de UTF-8 y la verificación de columnas obligatorias.
       → se recuperan dentro de la jerarquía de clases (método plantilla).
  C-9  Se lanzaban FileNotFoundError / ImportError en lugar de las
       excepciones del contrato. → ErrorLecturaFuente / ErrorFormatoFuente.
  C-10 Se eliminaron las funciones leer_csv / leer_json / leer_excel que usa
       carga_datos.py. → se conservan como una «fachada» de una línea.

Ideas clave para estudiar:
1. CLASE ABSTRACTA (ABC): `LectorBase` no se puede instanciar; obliga a cada
   subclase a implementar `_leer_filas`. Si una subclase lo olvida, Python
   lanza TypeError al crearla, no a mitad del procesamiento.
2. MÉTODO PLANTILLA (template method): `leer()` está escrito UNA sola vez en
   la clase base y define los pasos comunes (obtener filas → agregar
   `_origen` y `_fila`). Cada subclase solo sabe cómo partir SU formato.
   Así la salida es homogénea por construcción, no por disciplina.
3. DOS NIVELES DE FALLA:
   - Falla de TODO el archivo (no existe, no es UTF-8, JSON mal formado,
     faltan columnas): se lanza ErrorLecturaFuente o ErrorFormatoFuente.
   - Falla de UNA fila (columnas de más o de menos): la fila se MARCA con
     `_error_tecnico` y la lectura continúa. El Rol B la reporta como
     error técnico. Una fila rota no debe impedir leer las otras 622.
"""
# PEP 8: importaciones al inicio, agrupadas: estándar, terceros, proyecto.
import csv
import io
import json
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from src.exceptions.errores import ErrorFormatoFuente, ErrorLecturaFuente

# Columnas mínimas del registro canónico (docs/contratos_modulos.md).
COLUMNAS_OBLIGATORIAS = ("id", "tipo", "valor", "unidad")


# --------------------------------------------------------------------------
# Funciones auxiliares (el guion bajo indica «uso interno del módulo»)
# --------------------------------------------------------------------------
def _nombre_origen(archivo):
    """Nombre del archivo para la trazabilidad (`_origen`)."""
    if isinstance(archivo, (str, Path)):
        return Path(archivo).name
    nombre = getattr(archivo, "name", None)  # UploadedFile de Streamlit
    return Path(nombre).name if nombre else "memoria"


def _obtener_bytes(archivo):
    """REVISIÓN (C-7): ADAPTADOR que convierte cualquier entrada a bytes.

    La versión de los estudiantes hacía `os.path.exists(ruta)` y
    `open(ruta)`: funciona con una ruta, pero Streamlit entrega un objeto
    UploadedFile. Con `hasattr` se acepta «cualquier cosa que tenga
    .getvalue() o .read()» sin conocer su clase (duck typing).

    Además, la verificación «el archivo no existe» se hace AQUÍ, al leer,
    y no en el constructor: así crear el lector nunca falla y todos los
    errores de lectura salen por el mismo camino (ErrorLecturaFuente).
    """
    if isinstance(archivo, (str, Path)):
        try:
            return Path(archivo).read_bytes()
        except OSError as exc:  # incluye FileNotFoundError y PermissionError
            # REVISIÓN (C-9): excepción del contrato, no FileNotFoundError.
            # `from exc` conserva el error original como causa.
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


def _verificar_columnas(columnas, origen):
    """REVISIÓN (C-8): ErrorFormatoFuente si faltan columnas obligatorias."""
    faltantes = [c for c in COLUMNAS_OBLIGATORIAS if c not in columnas]
    if faltantes:
        raise ErrorFormatoFuente(
            f"{origen}: faltan las columnas obligatorias {', '.join(faltantes)}."
        )


# --------------------------------------------------------------------------
# Jerarquía de lectores (diseño propuesto por el Rol C)
# --------------------------------------------------------------------------
class LectorBase(ABC):
    """Interfaz común de los lectores.

    Uso:  LectorCSV("data/raw/temperatura.csv").leer()  -> list[dict]
          LectorCSV(uploaded_file).leer()               (Streamlit)
    """

    def __init__(self, archivo, nombre_origen=None):
        # REVISIÓN (C-7): se llama `archivo` y no `ruta_archivo` porque
        # puede ser una ruta, bytes o un objeto tipo archivo.
        self.archivo = archivo
        self.origen = nombre_origen or _nombre_origen(archivo)

    # -- métodos que reutilizan todas las subclases ------------------------
    def _obtener_bytes(self):
        return _obtener_bytes(self.archivo)

    def _obtener_texto(self):
        """bytes → texto. `utf-8-sig` elimina el BOM que agrega Excel al
        guardar CSV: con 'utf-8' el primer encabezado sería «\\ufeffid» y la
        columna «id» parecería faltar (temperatura.csv tiene BOM)."""
        try:
            return self._obtener_bytes().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ErrorLecturaFuente(
                f"{self.origen} no está codificado en UTF-8: {exc}"
            ) from exc

    # -- método plantilla -----------------------------------------------------
    def leer(self):
        """REVISIÓN (C-8): MÉTODO PLANTILLA. Pasos comunes a todos los formatos.

        Las subclases NO redefinen este método: implementan `_leer_filas`,
        que devuelve pares (numero_de_fila, diccionario). Aquí se agregan
        los metadatos, así ningún lector puede olvidarlos.
        """
        registros = []
        for numero_fila, registro in self._leer_filas():
            registro["_origen"] = self.origen
            registro["_fila"] = numero_fila
            registros.append(registro)
        return registros

    @abstractmethod
    def _leer_filas(self):
        """Cada formato devuelve una lista de (numero_fila, dict)."""


class LectorCSV(LectorBase):
    """Lee un CSV con encabezado."""

    def _leer_filas(self):
        # REVISIÓN (C-8): la versión de los estudiantes usaba csv.DictReader.
        # DictReader ESCONDE las filas irregulares: si sobran columnas las
        # guarda en la clave None y si faltan pone None en los valores. Con
        # csv.reader se compara el largo de cada fila con el encabezado.
        filas = csv.reader(io.StringIO(self._obtener_texto()))

        encabezado = next(filas, None)
        if not encabezado:
            raise ErrorFormatoFuente(f"{self.origen}: el archivo CSV está vacío.")
        encabezado = [columna.strip() for columna in encabezado]
        _verificar_columnas(encabezado, self.origen)

        resultado = []
        # enumerate(..., start=2): la fila 1 del archivo es el encabezado.
        for numero_fila, fila in enumerate(filas, start=2):
            if not any(celda.strip() for celda in fila):
                continue  # se ignoran las líneas en blanco
            if len(fila) != len(encabezado):
                # Falla de UNA fila: se marca y se sigue leyendo.
                # El Rol B la convierte en ErrorEstructuraRegistro.
                resultado.append((numero_fila, {
                    "id": fila[0] if fila else None,
                    "_error_tecnico": (
                        f"Fila irregular: tiene {len(fila)} columnas y se "
                        f"esperaban {len(encabezado)}."
                    ),
                }))
                continue
            resultado.append((numero_fila, dict(zip(encabezado, fila))))
        return resultado


class LectorJSON(LectorBase):
    """Lee un JSON con `[ {...}, ... ]` o `{"registros": [ {...}, ... ]}`."""

    def _leer_filas(self):
        try:
            datos = json.loads(self._obtener_texto())
        except json.JSONDecodeError as exc:
            raise ErrorLecturaFuente(
                f"{self.origen}: JSON mal formado en la línea {exc.lineno}, "
                f"columna {exc.colno} ({exc.msg})."
            ) from exc

        # REVISIÓN (C-8): presion.json usa la forma {"registros": [...]}.
        # La versión de los estudiantes hacía `[datos]` con cualquier dict:
        # el resultado era UN solo registro con la clave "registros" y los
        # 708 registros reales se perdían sin ningún mensaje de error.
        if isinstance(datos, dict) and isinstance(datos.get("registros"), list):
            datos = datos["registros"]
        if not isinstance(datos, list):
            raise ErrorFormatoFuente(
                f"{self.origen}: se esperaba una lista de registros o "
                f"{{\"registros\": [...]}} y se recibió {type(datos).__name__}."
            )

        resultado = []
        for posicion, elemento in enumerate(datos, start=1):
            if isinstance(elemento, dict):
                # dict(...) hace una copia para no modificar los datos leídos.
                resultado.append((posicion, dict(elemento)))
            else:
                # Un elemento que no es objeto JSON se marca, no detiene la lectura.
                resultado.append((posicion, {"_error_tecnico": (
                    f"Elemento JSON no es un objeto: {type(elemento).__name__}."
                )}))
        return resultado


class LectorExcel(LectorBase):
    """Lee la primera hoja de un archivo .xlsx."""

    def _leer_filas(self):
        try:
            tabla = pd.read_excel(
                io.BytesIO(self._obtener_bytes()),
                # dtype=object: pandas NO fuerza tipos; cada celda conserva el
                # tipo que tiene en Excel. Convertir es tarea del Rol B.
                dtype=object,
            )
        except (ValueError, OSError, KeyError) as exc:
            # Archivo dañado o que no es un Excel válido: falla de todo el archivo.
            raise ErrorLecturaFuente(
                f"{self.origen}: no es un archivo Excel válido ({exc})."
            ) from exc

        if tabla.empty and len(tabla.columns) == 0:
            raise ErrorFormatoFuente(f"{self.origen}: la hoja de Excel está vacía.")
        tabla.columns = [str(columna).strip() for columna in tabla.columns]
        _verificar_columnas(tabla.columns, self.origen)

        # pandas representa las celdas vacías como NaN (float). Se cambian
        # por None, igual que un `null` de JSON: ningún NaN viaja a los demás
        # módulos. (NaN != NaN, por eso un `valor is None` no lo detectaría.)
        # La idea ya estaba en la versión de los estudiantes; se agrega
        # astype(object) para que una columna numérica pueda guardar None.
        tabla = tabla.astype(object).where(tabla.notna(), None)

        # La fila 1 de Excel es el encabezado; el índice 0 de pandas es la fila 2.
        return [
            (indice + 2, registro)
            for indice, registro in enumerate(tabla.to_dict(orient="records"))
        ]


# --------------------------------------------------------------------------
# Fachada funcional (contrato original del Rol C, la usa carga_datos.py)
# --------------------------------------------------------------------------
# REVISIÓN (C-10): las clases son la implementación; estas funciones son la
# API pública estable. Quien solo necesita «leer un CSV» no tiene que saber
# que existe una jerarquía de clases.
def leer_csv(archivo):
    """Lee un CSV y devuelve list[dict] con `_origen` y `_fila`."""
    return LectorCSV(archivo).leer()


def leer_json(archivo):
    """Lee un JSON y devuelve list[dict] con `_origen` y `_fila`."""
    return LectorJSON(archivo).leer()


def leer_excel(archivo):
    """Lee un Excel (.xlsx) y devuelve list[dict] con `_origen` y `_fila`."""
    return LectorExcel(archivo).leer()
