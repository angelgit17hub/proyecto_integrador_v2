
"""Pruebas unitarias del Rol A: calidad de datos."""

import unittest

from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro


class TestNormalizacion(unittest.TestCase):

    def test_elimina_espacios(self):
        registro = {
            "id": " T001 ",
            "tipo": " TEMPERATURA ",
            "valor": " 25.5 ",
            "unidad": " °C "
        }

        resultado = normalizar_registro(registro)

        self.assertEqual(resultado["id"], "T001")
        self.assertEqual(resultado["tipo"], "temperatura")
        self.assertEqual(resultado["valor"], "25.5")
        self.assertEqual(resultado["unidad"], "°C")

    def test_no_modifica_original(self):
        registro = {
            "id": " T001 ",
            "tipo": " TEMPERATURA ",
            "valor": " 25.5 ",
            "unidad": " °C "
        }

        original = registro.copy()
        normalizar_registro(registro)

        self.assertEqual(registro, original)

    def test_devuelve_copia(self):
        registro = {"id": "T001"}

        resultado = normalizar_registro(registro)

        self.assertIsNot(resultado, registro)

    def test_rechaza_entrada_no_diccionario(self):
        with self.assertRaises(TypeError):
            normalizar_registro(["T001", "temperatura"])


class TestValidaciones(unittest.TestCase):

    def test_acepta_registro_valido(self):
        registro = {
            "id": "T001",
            "tipo": "temperatura",
            "valor": "25.5",
            "unidad": "\u00b0C"
        }

        valido, motivos = validar_registro(registro)

        self.assertTrue(valido)
        self.assertEqual(motivos, [])

    def test_rechaza_tipo_no_permitido(self):
        registro = {
            "id": "X001",
            "tipo": "viento",
            "valor": "20",
            "unidad": "km/h"
        }

        valido, motivos = validar_registro(registro)

        self.assertFalse(valido)
        self.assertTrue(any("Tipo de sensor" in m for m in motivos))

    def test_rechaza_tipo_que_no_es_texto(self):
        registro = {
            "id": "X001",
            "tipo": ["temperatura"],
            "valor": "25",
            "unidad": "\u00b0C"
        }

        valido, motivos = validar_registro(registro)

        self.assertFalse(valido)
        self.assertTrue(
            any("debe ser texto" in m for m in motivos)
        )

    def test_rechaza_valor_no_numerico(self):
        registro = {
            "id": "P001",
            "tipo": "presion",
            "valor": "abc",
            "unidad": "hPa"
        }

        valido, motivos = validar_registro(registro)

        self.assertFalse(valido)
        self.assertTrue(any("numérico" in m for m in motivos))

    def test_detecta_varios_errores(self):
        registro = {
            "id": "",
            "tipo": "viento",
            "valor": "abc",
            "unidad": "km/h"
        }

        valido, motivos = validar_registro(registro)

        self.assertFalse(valido)
        self.assertGreaterEqual(len(motivos), 3)

    def test_rechaza_unidad_incorrecta(self):
        registro = {
            "id": "T001",
            "tipo": "temperatura",
            "valor": "25.5",
            "unidad": "hPa"
        }

        valido, motivos = validar_registro(registro)

        self.assertFalse(valido)
        self.assertTrue(any("Unidad incorrecta" in m for m in motivos))

    def test_rechaza_nan(self):
        registro = {
            "id": "T001",
            "tipo": "temperatura",
            "valor": "NaN",
            "unidad": "\u00b0C"
        }

        valido, motivos = validar_registro(registro)

        self.assertFalse(valido)
        self.assertTrue(any("finito" in m for m in motivos))

    def test_rechaza_infinito(self):
        registro = {
            "id": "T002",
            "tipo": "temperatura",
            "valor": "inf",
            "unidad": "\u00b0C"
        }

        valido, motivos = validar_registro(registro)

        self.assertFalse(valido)
        self.assertTrue(any("finito" in m for m in motivos))

    def test_detecta_campos_ausentes(self):
        registro = {
            "id": "T003",
            "tipo": "temperatura"
        }

        valido, motivos = validar_registro(registro)

        self.assertFalse(valido)
        self.assertTrue(any("valor" in m for m in motivos))
        self.assertTrue(any("unidad" in m for m in motivos))


if __name__ == "__main__":
    unittest.main()


