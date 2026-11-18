"""Rol C: selección y unificación de fuentes (semana 12).

Punto único de entrada a los datos: quien llama no necesita saber si los
registros vienen de memoria, de un CSV, de un JSON o de un Excel.

REVISIÓN (semana 12, segunda entrega del Rol C — commit 75ebe15):
Los estudiantes reemplazaron `cargar_datos(...)` por la clase
`CargaDatosUnificada`. Se conserva la clase, pero había cuatro problemas:

  C-11 `from lectores import ...` → ModuleNotFoundError. Dentro de un paquete
       se importa con la ruta completa desde la raíz: `src.data.lectores`.
       Con este error NI la demostración en memoria abría en Streamlit.
  C-12 Se eliminó `cargar_datos(archivo, nombre_archivo)`, que es lo que
       llama src/services/datalab_service.py. Cambiar la firma de una función
       pública rompe a los demás roles: el contrato entre módulos se respeta
       (o se cambia en equipo, actualizando docs/contratos_modulos.md).
  C-13 Sin archivo ya no se cargaba la fuente en memoria (demostración).
  C-14 ValueError genérico y «.xls» aceptado: el proyecto instala openpyxl,
       que solo lee .xlsx. → ErrorFormatoFuente y tabla extensión → lector.
"""
from pathlib import Path

# REVISIÓN (C-11): importación absoluta desde la raíz del proyecto.
from src.data.fuentes_memoria import cargar_desde_memoria
from src.data.lectores import LectorCSV, LectorExcel, LectorJSON
from src.exceptions.errores import ErrorFormatoFuente

# REVISIÓN (C-14): tabla extensión → CLASE lectora, en lugar de if/elif.
# Las clases también son objetos: se guardan en un diccionario y se
# instancian después con LECTORES_POR_EXTENSION[ext](archivo).
# Para soportar un formato nuevo basta con crear la subclase y agregar una
# línea aquí (principio abierto/cerrado: abierto a extensión, cerrado a
# modificación). Es la misma idea que EVENTOS_TECNICOS en errores.py.
LECTORES_POR_EXTENSION = {
    "csv": LectorCSV,
    "json": LectorJSON,
    "xlsx": LectorExcel,
}


class CargaDatosUnificada:
    """Gestor centralizado de carga bajo un contrato común (diseño del Rol C).

    Uso:  CargaDatosUnificada("data/raw/presion.json").cargar()
          CargaDatosUnificada(uploaded_file, "humedad.xlsx").cargar()
    """

    def __init__(self, archivo, nombre_archivo=""):
        # REVISIÓN (C-7): `archivo` puede ser ruta, bytes o UploadedFile.
        # Si no se envía el nombre, se toma del atributo .name (Streamlit)
        # o de la propia ruta.
        self.archivo = archivo
        self.nombre_archivo = (
            nombre_archivo or getattr(archivo, "name", None) or str(archivo)
        )

    def obtener_lector(self):
        """Elige la clase lectora según la extensión del nombre."""
        # Path(...).suffix devuelve ".csv"; [1:] quita el punto.
        # Si no hay extensión, suffix es "" y el mensaje lo indica.
        extension = Path(str(self.nombre_archivo)).suffix.lower()[1:]
        clase_lector = LECTORES_POR_EXTENSION.get(extension)
        if clase_lector is None:
            # REVISIÓN (C-14): excepción del contrato, no ValueError.
            raise ErrorFormatoFuente(
                f"Formato de archivo no soportado: "
                f"'{extension or 'sin extensión'}'. "
                f"Se aceptan: {', '.join(LECTORES_POR_EXTENSION)}."
            )
        # POLIMORFISMO: quien recibe el lector solo llama .leer(); no le
        # importa si es CSV, JSON o Excel.
        return clase_lector(self.archivo, Path(str(self.nombre_archivo)).name)

    def cargar(self):
        """Devuelve los registros del archivo como list[dict]."""
        return self.obtener_lector().leer()


def cargar_datos(archivo=None, nombre_archivo=""):
    """Contrato público del Rol C (lo usa datalab_service.py).

    - Sin archivo → registros de la fuente en memoria (demostración).
    - Con archivo → delega en CargaDatosUnificada.
    """
    # REVISIÓN (C-12, C-13): se recupera la función que el servicio llama.
    if archivo is None:
        return cargar_desde_memoria()
    return CargaDatosUnificada(archivo, nombre_archivo).cargar()
