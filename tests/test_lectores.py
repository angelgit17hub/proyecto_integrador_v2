import json
import csv
import pytest
from data.carga_datos import CargaDatosUnificada

def test_lector_csv(tmp_path):
    # 1. Crear un archivo CSV temporal de prueba
    archivo_csv = tmp_path / "datos_prueba.csv"
    archivo_csv.write_text("id,tipo,unidad,valor\nreg_1,temperatura,celsius,24.5", encoding="utf-8")

    # 2. Ejecutar la carga unificada
    cargador = CargaDatosUnificada(str(archivo_csv))
    registros = cargador.cargar()

    # 3. Aserciones
    assert len(registros) == 1
    assert registros[0]["id"] == "reg_1"
    assert registros[0]["tipo"] == "temperatura"


def test_lector_json(tmp_path):
    # 1. Crear un archivo JSON temporal de prueba
    archivo_json = tmp_path / "datos_prueba.json"
    datos = [{"id": "reg_2", "tipo": "humedad", "unidad": "%", "valor": "60"}]
    archivo_json.write_text(json.dumps(datos), encoding="utf-8")

    # 2. Ejecutar la carga unificada
    cargador = CargaDatosUnificada(str(archivo_json))
    registros = cargador.cargar()

    # 3. Aserciones
    assert len(registros) == 1
    assert registros[0]["id"] == "reg_2"
    assert registros[0]["tipo"] == "humedad"


def test_archivo_no_encontrado():
    # Verificar que se lance una excepción si el archivo no existe
    cargador = CargaDatosUnificada("archivo_inexistente.csv")
    with pytest.raises(FileNotFoundError):
        cargador.cargar()


def test_formato_no_soportado(tmp_path):
    # Verificar que se lance un error con extensiones no válidas
    archivo_txt = tmp_path / "datos.txt"
    archivo_txt.write_text("datos de texto plano", encoding="utf-8")
    
    cargador = CargaDatosUnificada(str(archivo_txt))
    with pytest.raises(ValueError, match="Formato de archivo no soportado"):
        cargador.cargar()