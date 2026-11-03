# Entregas semanales y distribución de trabajo

Los porcentajes son una referencia de esfuerzo relativo entre los tres roles dentro de cada semana. Se busca una carga equilibrada en implementación, pruebas y documentación; no igualdad de líneas de código.

## Semana 10 — v1.0: normalización y validación
- A (33%): normalizar id/tipo/unidad/valor textual; validar campos, tipos, unidades y formato numérico. Archivos: `normalizacion.py`, `validaciones.py`.
- B (33%): integrar flujo de estados válido/inválido y coordinar la validación sin excepciones avanzadas. Archivos: `procesamiento.py`, `estados.py` (si se requiere).
- C (34%): preparar adaptador en memoria y fixtures con formatos variados. Archivos: `fuentes_memoria.py`, `fixtures_semana10.py`.
- Aceptación: los registros se normalizan, validan y clasifican; los inválidos quedan separados con motivos.

## Semana 11 — v1.1: excepciones y manejo de errores
- A (33%): mejorar mensajes y motivos de validación. Archivos: `validaciones.py`, `normalizacion.py`.
- B (34%): implementar excepciones, reporte y continuidad por registro. Archivos: `errores.py`, `procesamiento.py`.
- C (33%): construir escenarios de origen defectuoso y pruebas de estructura/fuente. Archivos: `escenarios_fuente.py`, pruebas de entrada.
- Aceptación: un error no detiene el lote; se identifica y contabiliza.

## Semana 12 — v1.2: lectura de archivos
- A (34%): validar y normalizar registros provenientes de archivos. Archivos: `normalizacion.py`, `validaciones.py`.
- B (33%): controlar errores de lectura, conversión y estructura. Archivos: `errores.py`, `procesamiento.py`.
- C (33%): implementar lectores CSV, JSON y Excel y unificar salida. Archivos: `lectores.py`, `carga_datos.py`.
- Aceptación: los tres datasets se cargan y procesan con el contrato común.

## Semana 13 — v1.3: refactorización
- A (33%): eliminar duplicidad y mejorar reglas de calidad. Archivos: `validation/`.
- B (34%): refactorizar procesamiento y trazabilidad. Archivos: `exceptions/`, `processing/`.
- C (33%): refactorizar lectores y carga uniforme. Archivos: `data/`.
- Aceptación: resultados equivalentes a v1.2; código más mantenible.

## Semana 14 — v1.4: pruebas y sustentación
- A (34%): pruebas de normalización, validación y casos límite. Archivo: `tests/test_calidad.py`.
- B (33%): pruebas de excepciones, continuidad e integración. Archivos: `tests/test_errores.py`, `tests/test_integracion.py`.
- C (33%): pruebas de lectura y calidad de entradas de archivos. Archivo: `tests/test_lectores.py`.
- Aceptación: pruebas completas ejecutadas, documentación actualizada y sustentación individual.

## Elementos transversales por integrante
Cada estudiante entrega rama semanal, commits, pruebas, Pull Request, evidencia y explicación individual. La integración de las tres ramas debe completar el 100% de la funcionalidad solicitada.
