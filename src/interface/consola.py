"""Presentación de resultados en consola."""
def mostrar_resumen(resumen):
    print("\n========== RESUMEN DATALAB ==========")
    print(f"Total: {resumen['total']}")
    print(f"BAJO: {resumen['bajos']} | NORMAL: {resumen['normales']} | ALTO: {resumen['altos']}")
    # Cada sensor tiene su propia unidad: se muestra un promedio por tipo.
    for tipo, promedio in resumen.get("promedio_por_sensor", {}).items():
        print(f"Promedio {tipo}: {promedio:.2f}")
    print("=====================================")
