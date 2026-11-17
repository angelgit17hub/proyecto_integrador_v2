from abc import ABC, abstractmethod
import csv
import json
import os

try:
    import pandas as pd
except ImportError:
    pd = None

class LectorBase(ABC):
    """Interfaz abstracta para unificar el comportamiento de los lectores."""
    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo
        self._validar_existencia()

    def _validar_existencia(self):
        if not os.path.exists(self.ruta_archivo):
            raise FileNotFoundError(f"El archivo no existe: {self.ruta_archivo}")

    @abstractmethod
    def leer(self) -> list:
        pass


class LectorCSV(LectorBase):
    def leer(self) -> list:
        with open(self.ruta_archivo, mode='r', encoding='utf-8') as archivo:
            return [dict(fila) for fila in csv.DictReader(archivo)]


class LectorJSON(LectorBase):
    def leer(self) -> list:
        with open(self.ruta_archivo, mode='r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            return datos if isinstance(datos, list) else [datos]


class LectorExcel(LectorBase):
    def leer(self) -> list:
        if pd is None:
            raise ImportError("Se requiere 'pandas' y 'openpyxl' para leer Excel.")
        df = pd.read_excel(self.ruta_archivo)
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient='records')
