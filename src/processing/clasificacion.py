"""Reglas pedagógicas de clasificación por tipo de sensor."""
def clasificar_valor(valor, tipo):
    if tipo == "temperatura":
        if valor < 18: return "BAJO"
        if valor <= 26: return "NORMAL"
        return "ALTO"
    if tipo == "presion":
        if valor < 1000: return "BAJO"
        if valor <= 1020: return "NORMAL"
        return "ALTO"
    if tipo == "humedad":
        if valor < 40: return "BAJO"
        if valor <= 60: return "NORMAL"
        return "ALTO"
    return "TIPO NO RECONOCIDO"
