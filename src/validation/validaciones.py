"""Rol A: reglas de validación de calidad de registros."""

import math

TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}

UNIDADES_POR_TIPO = {
    "temperatura": "\u00b0C",
    "presion": "hPa",
    "humedad": "%"
}


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
        elif registro[campo] is None or registro[campo] == "":
            motivos.append(f"El campo {campo} está vacío.")

    # 3. Comprobar el identificador.
    identificador = registro.get("id")

    if identificador is not None and not isinstance(identificador, str):
        motivos.append("El identificador debe ser texto.")

    # 4. Comprobar el tipo de sensor.
    tipo = registro.get("tipo")

    if tipo is not None and tipo != "":
        if not isinstance(tipo, str):
            motivos.append("El tipo de sensor debe ser texto.")
        elif tipo not in TIPOS_PERMITIDOS:
            motivos.append(f"Tipo de sensor no permitido: {tipo}.")

    # 5. Comprobar que el valor sea numérico y finito.
    valor = registro.get("valor")

    if valor is not None and valor != "":
        if isinstance(valor, bool):
            motivos.append("El valor debe ser numérico.")
        else:
            try:
                numero = float(valor)

                if not math.isfinite(numero):
                    motivos.append("El valor debe ser un número finito.")

            except (ValueError, TypeError):
                motivos.append("El valor debe ser numérico.")

    # 6. Comprobar la unidad correspondiente al sensor.
    unidad = registro.get("unidad")

    if (
    isinstance(tipo, str)
    and tipo in UNIDADES_POR_TIPO
    and unidad not in (None, "")
):
        unidad_esperada = UNIDADES_POR_TIPO[tipo]

        if unidad != unidad_esperada:
            motivos.append(
                f"Unidad incorrecta para {tipo}. "
                f"Se esperaba {unidad_esperada}."
            )

    # 7. Devolver todos los motivos encontrados.
    es_valido = len(motivos) == 0

    return es_valido, motivos
