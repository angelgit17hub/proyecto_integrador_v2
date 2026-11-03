# DataLab — Proyecto integrador (semanas 1–14)

Proyecto académico modular en Python para procesar y analizar datos sintéticos de sensores. El equipo desarrolla una única aplicación progresiva; cada entrega conserva las funcionalidades anteriores.

## Organización del equipo

Equipos de tres estudiantes con roles técnicos permanentes durante las semanas 10–14:

| Rol | Responsabilidad | Archivos principales |
|---|---|---|
| A — Calidad de datos | Normalización, estandarización, validación y motivos de rechazo. | `src/validation/normalizacion.py`, `validaciones.py` |
| B — Robustez | Excepciones, reporte de errores, continuidad del lote e integración del procesamiento. | `src/exceptions/errores.py`, `src/processing/procesamiento.py` |
| C — Fuentes | Adaptadores en memoria, lectura CSV/JSON/Excel y carga uniforme. | `src/data/fuentes_memoria.py`, `lectores.py`, `carga_datos.py` |

Las tres contribuciones son complementarias: A + B + C deben completar el 100 % de la funcionalidad solicitada en cada semana. La carga se equilibra en implementación, pruebas y documentación, no por cantidad de líneas de código.

## Interfaz gráfica

`src/interface/streamlit_app.py` y `src/services/datalab_service.py` son provistos por el docente. Streamlit incluye desde el día uno una demostración en memoria, tablas, indicadores, gráficos, descarga de resultados y selector gráfico de archivos. La lectura real de CSV/JSON/Excel se activa al integrar los lectores de la semana 12.

Los estudiantes no deben modificar `src/interface/` ni `src/services/`. La interfaz no contiene reglas de negocio.

## Estructura del proyecto

```text
DataLab/
├── src/
│   ├── main.py
│   ├── data/
│   │   ├── sensores.py
│   │   ├── fuentes_memoria.py       # Rol C
│   │   ├── lectores.py              # Rol C · semana 12
│   │   └── carga_datos.py           # Rol C · semana 12
│   ├── validation/
│   │   ├── normalizacion.py         # Rol A
│   │   └── validaciones.py          # Rol A
│   ├── exceptions/
│   │   └── errores.py               # Rol B
│   ├── processing/
│   │   ├── clasificacion.py         # Regla centralizada
│   │   ├── procesamiento.py        # Rol B
│   │   └── resumen.py
│   ├── services/
│   │   └── datalab_service.py       # Docente
│   └── interface/
│       ├── consola.py
│       └── streamlit_app.py         # Docente · 100 %
├── data/
│   ├── raw/                         # CSV, JSON y Excel
│   ├── processed/
│   └── output/
├── tests/
├── docs/
└── requirements.txt
```

## Ejecución

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m streamlit run src/interface/streamlit_app.py
```

La línea base por consola puede ejecutarse con:

```bash
python -m src.main
```

## Datasets

Se incluyen tres datasets sintéticos, cada uno con 500 registros:

- `data/raw/temperatura.csv`
- `data/raw/presion.json`
- `data/raw/humedad.xlsx`

Cada archivo contiene 24 incidencias intencionales (4,8 %): 8 valores faltantes, 8 extremos respecto del rango de generación y 8 valores no numéricos. No son mediciones reales ni estándares regulatorios.

## Evolución y entregas

| Semana | Versión | Rol A — Calidad | Rol B — Robustez | Rol C — Fuentes |
|---|---|---|---|---|
| 10 | v1.0 | Normalizar y validar campos. | Integrar estados válido/inválido. | Adaptador y escenarios de prueba en memoria. |
| 11 | v1.1 | Mejorar motivos de validación. | Excepciones, reporte y continuidad. | Escenarios de fuentes defectuosas. |
| 12 | v1.2 | Calidad de registros cargados. | Errores de lectura y conversión. | Lectores CSV, JSON y Excel. |
| 13 | v1.3 | Refactorizar reglas de calidad. | Refactorizar procesamiento y errores. | Refactorizar lectores y carga. |
| 14 | v1.4 | Pruebas de calidad. | Pruebas de errores e integración. | Pruebas de lectores y fuentes. |

La aceptación de cada entrega exige integrar las tres ramas, ejecutar pruebas conjuntas y conservar la funcionalidad anterior.

## Git: ramas semanales

Los roles son permanentes; las ramas se crean por semana.

Ejemplo:

```text
main
└── semana-10
    ├── s10-calidad-datos
    ├── s10-robustez
    └── s10-fuentes
```

Flujo obligatorio:

1. Crear `semana-XX` desde `main`.
2. Crear las tres ramas individuales desde `semana-XX`.
3. Desarrollar en los archivos asignados al rol.
4. Registrar commits pequeños y descriptivos.
5. Ejecutar pruebas y abrir Pull Request hacia `semana-XX`.
6. Revisar e integrar los tres Pull Requests.
7. Ejecutar pruebas de integración.
8. Abrir Pull Request de `semana-XX` hacia `main`.
9. Verificar que `main` quede estable y ejecutable.

Convención de commits:

- `feat(rol): descripción` — nueva funcionalidad.
- `fix(rol): descripción` — corrección.
- `test(rol): descripción` — pruebas.
- `docs(rol): descripción` — documentación.

Cada estudiante debe evidenciar commits de implementación y pruebas, y correcciones/documentación cuando correspondan. No se califica la cantidad de commits de forma aislada: se revisa su contenido y trazabilidad.

## Contratos entre módulos

Los registros utilizan las claves `id`, `tipo`, `valor` y `unidad`.

El procesamiento integrado devuelve:

```python
{
    "registros_validos": [],
    "registros_invalidos": [],
    "errores": [],
    "resumen": {}
}
```

- Los lectores entregan registros y no clasifican.
- El rol A normaliza y valida; la normalización devuelve una copia.
- El rol B coordina el procesamiento y evita que un error individual detenga el lote.
- La clasificación se mantiene centralizada en `clasificar_valor(valor, tipo)`.
- La interfaz consume el servicio de aplicación y no implementa reglas de negocio.

## Evaluación

- **40 % — Código entregado y funcionando:** funcionalidad integrada, pruebas, calidad, trazabilidad Git y ejecución.
- **60 % — Sustentación:** comprensión individual y grupal, explicación del rol, decisiones técnicas, pruebas, integración y demostración del flujo completo.

Un producto funcional no sustituye la sustentación. Cada integrante debe poder explicar su contribución y comprender el funcionamiento global de DataLab.

## Reglas de trabajo

- No trabajar directamente sobre `main`.
- No modificar unilateralmente los contratos de `docs/contratos_modulos.md`.
- No modificar `src/interface/` ni `src/services/`.
- No duplicar las reglas de clasificación.
- Resolver conflictos mediante revisión y coordinación, sin sobrescribir el trabajo de otro integrante.
- Mantener actualizado el README y las evidencias de cada entrega.
