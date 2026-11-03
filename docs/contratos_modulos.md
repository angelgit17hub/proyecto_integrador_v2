# Contratos entre módulos

## Registro canónico
Todos los orígenes deben entregar diccionarios con estas claves:
`id`, `tipo`, `valor`, `unidad`.
El valor puede llegar como texto desde archivos; la conversión y validación corresponden al rol A dentro del contrato acordado.

## Rol C — fuentes
- `cargar_desde_memoria() -> list[dict]`
- `leer_csv(archivo) -> list[dict]`
- `leer_json(archivo) -> list[dict]`
- `leer_excel(archivo) -> list[dict]`
Los lectores no clasifican ni aplican reglas de calidad. Reportan errores de lectura mediante el contrato de excepciones.

## Rol A — calidad
- `normalizar_registro(registro) -> dict`
- `validar_registro(registro) -> tuple[bool, list[str]]`
La normalización devuelve una copia y no altera el objeto recibido. La validación devuelve todos los motivos encontrados.

## Rol B — procesamiento y robustez
`procesar_registros(registros) -> dict` con las claves:
- `registros_validos`: lista de registros normalizados, numéricos y clasificados.
- `registros_invalidos`: lista de registros con motivos de validación.
- `errores`: lista de incidencias técnicas.
- `resumen`: indicadores calculados sobre los registros válidos.

El error de un registro no debe detener el lote completo. No duplicar la clasificación: importar `clasificar_valor(valor, tipo)`.

## Interfaz docente
Streamlit consume el servicio de aplicación. No implementa reglas de negocio. Los estudiantes no modifican `src/interface/` ni `src/services/`.
