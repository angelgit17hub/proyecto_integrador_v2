"""Rol A: normalización y estandarización de registros.

Contrato:
- Recibir un diccionario.
- Devolver una copia normalizada.
- No modificar el registro original.
"""

def normalizar_registro(registro):
    # 1. Comprobar que recibimos un diccionario.
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")

    # 2. Crear una copia para proteger el registro original.
    registro_normalizado = registro.copy()

    # 3. Quitar espacios de los campos textuales.
    campos = ("id", "tipo", "unidad", "valor")

    for campo in campos:
        valor = registro_normalizado.get(campo)

        if isinstance(valor, str):
            registro_normalizado[campo] = valor.strip()

    # 4. Convertir el tipo a minúsculas.
    if isinstance(registro_normalizado.get("tipo"), str):
        registro_normalizado["tipo"] = (
            registro_normalizado["tipo"].lower()
        )

    # 5. Devolver el registro normalizado.
    return registro_normalizado

