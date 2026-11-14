"""Rol A: reglas de validación de calidad de registros.

REVISIÓN (semanas 10–12): se conservó la estructura del estudiante (pasos 1
a 7). Se agregaron la detección de NaN, motivos más precisos (semana 11) y
el control de rango plausible para datos de archivos (semana 12). Cada
cambio está marcado con «# REVISIÓN».
"""

import math

TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}

UNIDADES_POR_TIPO = {
    "temperatura": "°C",
    "presion": "hPa",
    "humedad": "%"
}

# REVISIÓN (A-4): rangos de PLAUSIBILIDAD por tipo de sensor.
# Responden a la pregunta «¿el dato es creíble?». 999 °C o 150 % de humedad
# son números bien escritos, pero no son mediciones posibles para estos
# sensores. Los README del proyecto indican que estos rangos viven aquí.
#
# Validar NO es clasificar: la clasificación BAJO/NORMAL/ALTO sigue
# centralizada en src/processing/clasificacion.py y no se duplica.
#
# Los límites salen del análisis de los datasets: las lecturas normales están
# entre 2 y 42 °C, entre 851 y 1080 hPa y entre 5 y 95 %; todas las
# incidencias extremas (-25, 999 °C; 650, 1500 hPa; -15, 150 %) quedan fuera.
# Son límites pedagógicos para datos sintéticos, no estándares reales.
RANGOS_PLAUSIBLES = {
    "temperatura": (-10.0, 50.0),
    "presion": (800.0, 1100.0),
    "humedad": (0.0, 100.0),
}


def _esta_vacio(contenido):
    """REVISIÓN (A-3): None, texto vacío o NaN cuentan como «vacío».

    NaN es el único valor distinto de sí mismo (x != x). Sin esta regla, una
    celda vacía de Excel producía el motivo «número no finito» en lugar de
    «campo vacío»: el mismo problema con dos motivos distintos según el origen.
    """
    if contenido is None or contenido == "":
        return True
    return isinstance(contenido, float) and contenido != contenido


def validar_registro(registro):
    """Devuelve (es_valido: bool, motivos: list[str])."""

    motivos = []

    # 1. Comprobar que recibimos un diccionario.
    if not isinstance(registro, dict):
        return False, ["El registro debe ser un diccionario."]

    # 2. Comprobar los campos obligatorios.
    campos_obligatorios = ("id", "tipo", "valor", "unidad")

    for campo in campos_obligatorios:
        if campo not in registro:
            motivos.append(f"Falta el campo obligatorio: {campo}.")
        # REVISIÓN (A-3): se usa _esta_vacio para detectar también NaN.
        elif _esta_vacio(registro[campo]):
            motivos.append(f"El campo {campo} está vacío.")

    # 3. Comprobar el identificador.
    identificador = registro.get("id")

    # REVISIÓN: se omite si ya se reportó vacío, para no repetir el motivo.
    if not _esta_vacio(identificador) and not isinstance(identificador, str):
        motivos.append(
            f"El identificador debe ser texto: se recibió "
            f"{type(identificador).__name__}."
        )

    # 4. Comprobar el tipo de sensor.
    tipo = registro.get("tipo")
    # REVISIÓN: bandera que indica si el tipo es uno de los permitidos.
    # Se usa en los pasos 5 y 6 para no evaluar reglas que dependen del tipo.
    tipo_es_conocido = isinstance(tipo, str) and tipo in TIPOS_PERMITIDOS

    if not _esta_vacio(tipo):
        if not isinstance(tipo, str):
            motivos.append("El tipo de sensor debe ser texto.")
        elif not tipo_es_conocido:
            # REVISIÓN (A-5): el motivo indica qué tipos sí se aceptan.
            motivos.append(
                f"Tipo de sensor no permitido: {tipo}. "
                f"Se esperaba uno de: {', '.join(sorted(TIPOS_PERMITIDOS))}."
            )

    # 5. Comprobar que el valor sea numérico y finito.
    valor = registro.get("valor")

    if not _esta_vacio(valor):
        if isinstance(valor, bool):
            # REVISIÓN (A-5): True/False son int en Python; se explica el porqué.
            motivos.append(f"El valor no es numérico: {valor} es booleano.")
        else:
            try:
                numero = float(valor)

                if not math.isfinite(numero):
                    motivos.append(f"El valor no es un número finito: {valor}.")

                # REVISIÓN (A-4): rango plausible. Solo se evalúa si el
                # número es finito y el tipo es conocido (si no, no hay rango
                # con qué comparar y el motivo del tipo ya quedó registrado).
                elif tipo_es_conocido:
                    minimo, maximo = RANGOS_PLAUSIBLES[tipo]
                    if numero < minimo or numero > maximo:
                        motivos.append(
                            f"Valor fuera del rango plausible para {tipo}: "
                            f"{numero:g} (se acepta entre {minimo:g} y "
                            f"{maximo:g} {UNIDADES_POR_TIPO[tipo]})."
                        )

            except (ValueError, TypeError):
                # REVISIÓN (A-5): el motivo muestra el dato recibido
                # (por ejemplo 'N/A' o 'ERROR_SENSOR'). Un motivo preciso
                # permite corregir la fuente; «debe ser numérico» no dice qué llegó.
                motivos.append(f"El valor no es numérico: {valor!r}.")

    # 6. Comprobar la unidad correspondiente al sensor.
    unidad = registro.get("unidad")

    if tipo_es_conocido and not _esta_vacio(unidad):
        unidad_esperada = UNIDADES_POR_TIPO[tipo]

        if unidad != unidad_esperada:
            # REVISIÓN (A-5): se informa qué unidad llegó y cuál se esperaba.
            motivos.append(
                f"Unidad incorrecta para {tipo}: se recibió {unidad!r}. "
                f"Se esperaba {unidad_esperada}."
            )

    # 7. Devolver todos los motivos encontrados.
    es_valido = len(motivos) == 0

    return es_valido, motivos
