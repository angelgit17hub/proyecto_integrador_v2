"""Punto de entrada de la versión de consola."""
from src.data.fuentes_memoria import cargar_desde_memoria
from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen
from src.interface.consola import mostrar_resumen

def main():
    registros = cargar_desde_memoria()
    resultados = []
    for registro in registros:
        copia = registro.copy()
        copia["clasificacion"] = clasificar_valor(copia["valor"], copia["tipo"])
        resultados.append(copia)
    mostrar_resumen(generar_resumen(resultados))

if __name__ == "__main__":
    main()
