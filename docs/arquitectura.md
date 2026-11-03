# Arquitectura de DataLab

## Capas
1. Fuentes (`src/data`): entrega registros con estructura canónica.
2. Calidad (`src/validation`): normaliza y valida.
3. Procesamiento (`src/processing`): clasifica y calcula resultados.
4. Robustez (`src/exceptions`): define y reporta errores.
5. Servicio (`src/services`): fachada para la interfaz, provista por el docente.
6. Interfaz (`src/interface`): consola y Streamlit, provistas por el docente.

## Reglas
- La clasificación está centralizada en `clasificacion.py`.
- La interfaz no contiene reglas de negocio.
- Los lectores no normalizan ni clasifican.
- La validación no depende del origen de los datos.
- El procesamiento consume el contrato común y continúa ante errores individuales.
