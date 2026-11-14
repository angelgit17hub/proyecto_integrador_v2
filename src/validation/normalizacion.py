"""Rol A: normalización y estandarización de registros.

Contrato:
- Recibir un diccionario.
- Devolver una copia normalizada.
- No modificar el registro original.

REVISIÓN (semanas 10–12): se conservó la estructura original del estudiante
(pasos 1 a 5) y se agregaron los pasos de estandarización que pide la guía:
«normalizar identificadores, tipos, UNIDADES y valores». Cada cambio está
marcado con el comentario «# REVISIÓN» para poder buscarlo con Ctrl+F.
"""

# REVISIÓN (A-1): tabla de equivalencias de unidades.
# Un diccionario reemplaza una larga cadena de if/elif: para aceptar una
# variante nueva basta con agregar una línea. Las claves están escritas en
# minúsculas y sin espacios, porque así se buscan (ver paso 5).
# Si una unidad NO está en la tabla, se deja tal como llegó y la validación
# explica el motivo del rechazo: normalizar no es aceptar cualquier cosa.
EQUIVALENCIAS_UNIDAD = {
    "°c": "°C",
    "ºc": "°C",          # «º» (ordinal) se confunde a menudo con «°» (grado)
    "c": "°C",
    "celsius": "°C",
    "gradoscelsius": "°C",
    "hpa": "hPa",
    "hectopascal": "hPa",
    "hectopascales": "hPa",
    "%": "%",
    "porcentaje": "%",
}

# REVISIÓN (A-2): tabla de traducción para quitar tildes en una sola pasada.
# str.maketrans crea la tabla y str.translate la aplica a toda la cadena.
# Así "Presión" -> "presion", que es como está escrito en TIPOS_PERMITIDOS.
SIN_TILDES = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")


def _es_nan(valor):
    """REVISIÓN (A-3): indica si un valor es NaN (Not a Number).

    pandas representa las celdas vacías de Excel como NaN (un float).
    NaN es el único valor que NO es igual a sí mismo, por eso
    `valor != valor` es verdadero solo para NaN.
    """
    return isinstance(valor, float) and valor != valor


def normalizar_registro(registro):
    # 1. Comprobar que recibimos un diccionario.
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")

    # 2. Crear una copia para proteger el registro original.
    registro_normalizado = registro.copy()

    # REVISIÓN (A-3): un NaN (celda vacía de Excel) se convierte en None.
    # Así la validación reporta «campo vacío» sin importar si el dato vino
    # de CSV, JSON o Excel. La arquitectura lo exige: «la validación no
    # depende del origen de los datos». Es defensa en profundidad: aunque el
    # Rol C también evita los NaN, el Rol A se protege por su cuenta.
    for campo in ("id", "tipo", "unidad", "valor"):
        if _es_nan(registro_normalizado.get(campo)):
            registro_normalizado[campo] = None

    # 3. Quitar espacios de los campos textuales.
    campos = ("id", "tipo", "unidad", "valor")

    for campo in campos:
        valor = registro_normalizado.get(campo)

        if isinstance(valor, str):
            registro_normalizado[campo] = valor.strip()

    # REVISIÓN (A-2): estandarizar el identificador.
    # "p101" y "P101" deben representar el mismo sensor. Un id numérico
    # (por ejemplo, 101 leído desde Excel) se convierte a texto. Se excluye
    # bool porque en Python True/False son int y no son identificadores.
    identificador = registro_normalizado.get("id")
    if isinstance(identificador, int) and not isinstance(identificador, bool):
        registro_normalizado["id"] = str(identificador)
    if isinstance(registro_normalizado.get("id"), str):
        registro_normalizado["id"] = registro_normalizado["id"].upper()

    # 4. Convertir el tipo a minúsculas.
    if isinstance(registro_normalizado.get("tipo"), str):
        registro_normalizado["tipo"] = (
            registro_normalizado["tipo"].lower()
            # REVISIÓN (A-2): además se quitan las tildes ("presión" -> "presion").
            .translate(SIN_TILDES)
        )

    # REVISIÓN (A-1): 5. Estandarizar la unidad con la tabla de equivalencias.
    # Se busca en minúsculas y sin espacios internos ("H Pa" -> "hpa").
    # .get(clave, valor_por_defecto) devuelve la unidad original si no hay
    # equivalencia, para que la validación pueda rechazarla con su motivo.
    if isinstance(registro_normalizado.get("unidad"), str):
        clave = registro_normalizado["unidad"].lower().replace(" ", "")
        registro_normalizado["unidad"] = EQUIVALENCIAS_UNIDAD.get(
            clave, registro_normalizado["unidad"]
        )

    # REVISIÓN (A-6): 6. Coma decimal en valores de texto ("21,5" -> "21.5").
    # La regla es CONSERVADORA: solo actúa si hay exactamente una coma y
    # ningún punto. "1.013,2" se deja igual y la validación lo rechaza:
    # normalizar no debe inventar datos. El valor sigue siendo texto; la
    # conversión a número la hace el Rol B después de validar.
    valor = registro_normalizado.get("valor")
    if isinstance(valor, str) and valor.count(",") == 1 and "." not in valor:
        registro_normalizado["valor"] = valor.replace(",", ".")

    # 7. Devolver el registro normalizado.
    return registro_normalizado
