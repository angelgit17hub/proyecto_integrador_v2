# Distribución permanente de roles

## Rol A — Calidad de datos
Responsabilidad: normalización, estandarización y validación.
Archivos principales: `src/validation/normalizacion.py`, `src/validation/validaciones.py`.
Pruebas: `tests/test_calidad.py`.

## Rol B — Robustez y errores
Responsabilidad: excepciones, aislamiento de fallos, reporte y continuidad del procesamiento.
Archivos principales: `src/exceptions/errores.py`, `src/processing/procesamiento.py`.
Pruebas: `tests/test_errores.py`, `tests/test_integracion.py`.

## Rol C — Integración de fuentes
Responsabilidad: adaptadores de fuentes, lectores CSV/JSON/Excel y carga uniforme.
Archivos principales: `src/data/fuentes_memoria.py`, `src/data/lectores.py`, `src/data/carga_datos.py`.
Pruebas: `tests/test_lectores.py`.

Los roles son permanentes durante semanas 10–14. Los estudiantes no intercambian la propiedad técnica de los módulos, aunque todos deben comprender el sistema completo.
