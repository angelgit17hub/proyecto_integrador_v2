import os
from lectores import LectorCSV, LectorJSON, LectorExcel

class CargaDatosUnificada:
    """
    Gestor centralizado para la carga de datos desde diferentes fuentes de archivos
    bajo un contrato común.
    """
    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo

    def cargar(self) -> list:
        """
        Detecta la extensión del archivo, selecciona el lector adecuado
        y retorna los registros unificados.
        """
        _, extension = os.path.splitext(self.ruta_archivo)
        extension = extension.lower()

        lector = None
        if extension == '.csv':
            lector = LectorCSV(self.ruta_archivo)
        elif extension == '.json':
            lector = LectorJSON(self.ruta_archivo)
        elif extension in ['.xls', '.xlsx']:
            lector = LectorExcel(self.ruta_archivo)
        else:
            raise ValueError(f"Formato de archivo no soportado: {extension}")

        return lector.leer()
