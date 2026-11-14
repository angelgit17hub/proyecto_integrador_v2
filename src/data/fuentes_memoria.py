"""Rol C: adaptador de fuentes en memoria.

REVISIÓN (semanas 10–11): las funciones de escenarios estaban sin
implementar (NotImplementedError). Se distinguen dos tipos de escenario:

- preparar_registros_prueba()      → DATOS DE MALA CALIDAD (semana 10).
  Los normaliza y, si hace falta, los rechaza el Rol A
  (van a registros_invalidos con motivos).
- preparar_escenarios_defectuosos() → FUENTES DEFECTUOSAS (semana 11).
  Los detecta el Rol B como fallas técnicas (van a errores con categoría).
"""
from src.data.sensores import obtener_registros


def cargar_desde_memoria():
    """Fuente de datos funcional desde la primera entrega."""
    return obtener_registros()


def preparar_registros_prueba():
    """Rol C: escenarios adicionales de entrada para pruebas de semana 10."""
    # TODO C-S10-01: construir registros con espacios, mayúsculas y formatos diversos.
    # TODO C-S10-02: construir casos incompletos y tipos no reconocidos.
    # TODO C-S10-03: no alterar los 12 registros base.
    #
    # REVISIÓN (C-2): implementación de los TODO C-S10-01 a C-S10-03.
    # Los ids usan la serie 1xx para no confundirse con los 12 registros base.
    # C-S10-03: se devuelve una lista NUEVA; obtener_registros() crea sus
    # diccionarios en cada llamada, así que los 12 registros base no se alteran.

    # C-S10-01: formatos diversos que la normalización debe corregir.
    # Todos deberían quedar VÁLIDOS después de normalizar.
    formatos_diversos = [
        {"id": " t101 ", "tipo": " TEMPERATURA ", "valor": " 21.5 ", "unidad": " °C "},
        {"id": "P101", "tipo": "Presión", "valor": "1013", "unidad": "HPA"},
        {"id": "h101", "tipo": "Humedad", "valor": "55,5", "unidad": "porcentaje"},
        {"id": "T102", "tipo": "temperatura", "valor": 19, "unidad": "ºc"},
    ]

    # C-S10-02: casos incompletos y tipos no reconocidos.
    # Todos deberían quedar INVÁLIDOS, cada uno con sus motivos.
    casos_invalidos = [
        {"id": "T103", "tipo": "temperatura", "unidad": "°C"},                # sin valor
        {"id": "", "tipo": "humedad", "valor": 40, "unidad": "%"},             # id vacío
        {"id": "X101", "tipo": "viento", "valor": 12, "unidad": "km/h"},       # tipo no reconocido
        {"id": "T104", "tipo": "temperatura", "valor": "N/A", "unidad": "°C"}, # no numérico
        {"id": "P102", "tipo": "presion", "valor": 1013, "unidad": "°C"},      # unidad incorrecta
        {"id": "H102", "tipo": "humedad", "valor": 150, "unidad": "%"},        # fuera de rango
    ]

    return cargar_desde_memoria() + formatos_diversos + casos_invalidos


def preparar_escenarios_defectuosos():
    """REVISIÓN (C-3, semana 11): escenarios de FUENTES DEFECTUOSAS.

    Requisito S11 del Rol C: «escenarios de fuentes defectuosas».
    Simulan lo que entrega una fuente con fallas técnicas. Al procesarlos,
    2 registros deben ser válidos y 4 deben quedar en `errores`, sin que
    ninguno detenga el lote.
    """
    return [
        {"id": "T201", "tipo": "temperatura", "valor": 22.0, "unidad": "°C"},
        # Evento técnico simulado del sensor (igual que en los datasets).
        {"id": "T202", "tipo": "temperatura", "valor": 23.0, "unidad": "°C",
         "observacion_tecnica": "SIMULACION_TIMEOUT_SENSOR"},
        # Fila que un lector no pudo leer bien (columnas de más o de menos).
        {"id": "P201", "_error_tecnico": "Fila con columnas de más o de menos",
         "_origen": "escenario_memoria", "_fila": 3},
        # La fuente entregó texto en lugar de un diccionario.
        "P202;presion;1010;hPa",
        # La fuente entregó un registro vacío.
        None,
        {"id": "H201", "tipo": "humedad", "valor": 50.0, "unidad": "%"},
    ]


# REVISIÓN (buena práctica): nunca dejar print() en el nivel superior de un módulo: se
# ejecuta cada vez que otro módulo hace import (Streamlit, pruebas, consola).
# Para probar a mano se usa este bloque, que solo corre con
# `python -m src.data.fuentes_memoria`.
if __name__ == "__main__":
    print(len(cargar_desde_memoria()), "registros base")
    print(len(preparar_registros_prueba()), "registros de prueba")
    print(len(preparar_escenarios_defectuosos()), "escenarios defectuosos")
