"""Presentación de resultados en consola."""
def mostrar_resumen(resumen):
    print("\\n========== RESUMEN DATALAB ==========")
    print(f"Total: {resumen['total']}")
    print(f"BAJO: {resumen['bajos']} | NORMAL: {resumen['normales']} | ALTO: {resumen['altos']}")
    print(f"Promedio: {resumen['promedio']:.2f}")
    print("=====================================")
