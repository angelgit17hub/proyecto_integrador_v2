import unittest
from src.data.fuentes_memoria import cargar_desde_memoria, preparar_registros_prueba
from src.processing.procesamiento import procesar_registros
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro

class DataLabTests(unittest.TestCase):
    def test_normalizacion_no_modifica_original(self):
        original={"id":" A1 ","tipo":" TEMPERATURA ","valor":" 20 ","unidad":" °C "}
        copia=normalizar_registro(original)
        self.assertEqual(copia["tipo"],"temperatura")
        self.assertEqual(original["tipo"]," TEMPERATURA ")

    def test_validacion_acumula_motivos(self):
        ok,motivos=validar_registro({"id":"","tipo":"otro","valor":"x","unidad":""})
        self.assertFalse(ok); self.assertGreaterEqual(len(motivos),3)

    def test_lote_continua_y_separa_resultados(self):
        r=procesar_registros(preparar_registros_prueba())
        self.assertGreater(len(r["registros_validos"]),0)
        self.assertGreater(len(r["registros_invalidos"]),0)
        self.assertEqual(r["resumen"]["total"],len(r["registros_validos"]))

    def test_memoria_base(self):
        r=procesar_registros(cargar_desde_memoria())
        self.assertEqual(len(r["registros_validos"]),12)
        self.assertEqual(len(r["registros_invalidos"]),0)


    def test_evento_tecnico_no_detiene_el_lote(self):
        registros = [
            {"id": "T-1", "tipo": "temperatura", "valor": 22, "unidad": "°C"},
            {"id": "T-2", "tipo": "temperatura", "valor": 23, "unidad": "°C",
             "observacion_tecnica": "SIMULACION_TIMEOUT_SENSOR"},
            {"id": "T-3", "tipo": "temperatura", "valor": 24, "unidad": "°C"},
        ]
        resultado = procesar_registros(registros)
        self.assertEqual(len(resultado["registros_validos"]), 2)
        self.assertEqual(len(resultado["errores"]), 1)
        self.assertEqual(resultado["errores"][0]["categoria"], "TIMEOUT_SENSOR")

    def test_error_estructural_individual_no_detiene_lote(self):
        registros = [
            {"id": "P-1", "tipo": "presion", "valor": 1012, "unidad": "hPa"},
            {"id": "P-2", "_error_tecnico": "Fila irregular", "_origen": "CSV", "_fila": 3},
            {"id": "P-3", "tipo": "presion", "valor": 1015, "unidad": "hPa"},
        ]
        resultado = procesar_registros(registros)
        self.assertEqual(len(resultado["registros_validos"]), 2)
        self.assertEqual(len(resultado["errores"]), 1)
        self.assertEqual(resultado["errores"][0]["categoria"], "ESTRUCTURA_REGISTRO")

if __name__ == "__main__": unittest.main()
