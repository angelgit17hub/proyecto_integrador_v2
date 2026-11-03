"""Cálculo de indicadores a partir de registros clasificados."""
def generar_resumen(registros):
    altos = normales = bajos = 0
    suma = 0.0
    existe_alto = False
    por_sensor = {}

    for registro in registros:
        categoria = registro["clasificacion"]
        valor = float(registro["valor"])
        tipo = registro["tipo"]
        suma += valor

        if categoria == "ALTO":
            altos += 1
            existe_alto = True
        elif categoria == "NORMAL":
            normales += 1
        elif categoria == "BAJO":
            bajos += 1

        por_sensor.setdefault(tipo, {"ALTO": 0, "NORMAL": 0, "BAJO": 0})
        if categoria in por_sensor[tipo]:
            por_sensor[tipo][categoria] += 1

    total = len(registros)
    return {
        "altos": altos, "normales": normales, "bajos": bajos,
        "suma": suma, "existe_alto": existe_alto, "total": total,
        "promedio": suma / total if total else 0.0,
        "por_sensor": por_sensor,
    }
