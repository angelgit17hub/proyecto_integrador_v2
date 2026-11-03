"""Rol A: reglas de validación de calidad de registros."""
TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}

def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str])."""
    # TODO A-S10-05: validar campos obligatorios: id, tipo, valor y unidad.
    # TODO A-S10-06: validar tipo permitido.
    # TODO A-S10-07: validar que valor tenga formato numérico admitido.
    # TODO A-S10-08: definir reglas de unidad por tipo de sensor.
    # TODO A-S10-09: devolver todos los motivos encontrados, no solo el primero.
    raise NotImplementedError("Pendiente: implementación del rol A, semana 10")
