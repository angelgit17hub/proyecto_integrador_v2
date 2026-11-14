"""Interfaz gráfica docente de DataLab.

Tablero de análisis para una o varias fuentes (CSV, JSON, Excel) o la
demostración en memoria. Esta capa solo consume el servicio de aplicación y el
contrato de `procesar_registros` (registros_validos, registros_invalidos,
errores, resumen). No implementa reglas de calidad ni de clasificación: las
estadísticas que calcula (cuartiles, desviación, atípicos por IQR) son
descriptivas y sirven solo para presentar resultados.
"""
import io
import itertools
import math
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# `streamlit run src/interface/streamlit_app.py` solo agrega la carpeta del
# script a sys.path; se añade la raíz del proyecto para poder importar `src`.
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from src.services.datalab_service import ejecutar_demo, ejecutar_archivo  # noqa: E402

# --------------------------------------------------------------------------
# Configuración visual
# --------------------------------------------------------------------------
CARPETA_EJEMPLOS = RAIZ_PROYECTO / "data" / "raw"
EXTENSIONES = ["csv", "json", "xlsx"]

ORDEN_CLASIFICACION = ["BAJO", "NORMAL", "ALTO"]
# Escala divergente: frío (bajo) · neutro (normal) · cálido (alto).
COLOR_CLASIFICACION = {"BAJO": "#2a78d6", "NORMAL": "#9c9b95", "ALTO": "#e34948"}

ORDEN_ESTADO = ["Válidos", "Inválidos", "Errores técnicos"]
# Colores de estado (bueno · advertencia · crítico); siempre con etiqueta.
COLOR_ESTADO = {"Válidos": "#0ca30c", "Inválidos": "#fab219", "Errores técnicos": "#d03b3b"}

# Color fijo por tipo de sensor (no depende del orden de carga).
COLOR_SENSOR = {"temperatura": "#2a78d6", "presion": "#eb6834", "humedad": "#1baf7a"}
COLOR_SENSOR_OTRO = "#6250d6"
COLOR_RECHAZADAS = "#9c9b95"


def color_sensor(tipo):
    return COLOR_SENSOR.get(str(tipo), COLOR_SENSOR_OTRO)


def estilo(fig, alto=340, leyenda=True):
    """Aplica un estilo sobrio y homogéneo a todas las figuras."""
    fig.update_layout(
        height=alto,
        margin=dict(l=8, r=8, t=56, b=8),
        title_font_size=15,
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None),
        barcornerradius=4,
        bargap=0.3,
        hoverlabel=dict(font_size=12),
    )
    fig.update_xaxes(showgrid=False, title=None)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zeroline=False)
    return fig


_CONTADOR_GRAFICOS = itertools.count()


def mostrar(fig):
    # Clave única por ejecución: evita IDs duplicados si dos archivos generan figuras idénticas.
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False},
                    key=f"grafico_{next(_CONTADOR_GRAFICOS)}")


# --------------------------------------------------------------------------
# Utilidades de presentación (no son reglas de negocio)
# --------------------------------------------------------------------------
def a_numero(valor):
    """Intenta leer un número solo para graficar; si no puede, devuelve None."""
    if valor is None or isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        numero = float(valor)
    else:
        texto = str(valor).strip()
        if "," in texto and "." not in texto:
            texto = texto.replace(",", ".")
        try:
            numero = float(texto)
        except ValueError:
            return None
    return numero if math.isfinite(numero) else None


def resumir_motivo(motivo):
    """Agrupa motivos similares quitando el detalle posterior a ':' o '. '."""
    texto = str(motivo).split(":")[0].split(". ")[0]
    return texto.strip().rstrip(".")[:90] or "Sin detalle"


def limites_iqr(serie):
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    rango = q3 - q1
    return q1 - 1.5 * rango, q3 + 1.5 * rango


def para_mostrar(df):
    """Oculta metadatos internos y renombra los de trazabilidad."""
    if df.empty:
        return df
    renombres = {"_origen": "origen", "_fila": "fila"}
    columnas = [c for c in df.columns if not str(c).startswith("_") or c in renombres]
    return df[columnas].rename(columns=renombres)


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


# --------------------------------------------------------------------------
# Carga y procesamiento de fuentes
# --------------------------------------------------------------------------
class ArchivoEnMemoria(io.BytesIO):
    """BytesIO con atributo `name`, igual que los archivos de Streamlit."""

    def __init__(self, contenido, nombre):
        super().__init__(contenido)
        self.name = nombre


def procesar_fuente(nombre, contenido):
    try:
        return {"nombre": nombre, "resultado": ejecutar_archivo(ArchivoEnMemoria(contenido, nombre), nombre)}
    except Exception as exc:  # El fallo de un archivo no detiene a los demás.
        return {"nombre": nombre, "error": f"{type(exc).__name__}: {exc}"}


def construir_marcos(nombre, resultado):
    """Convierte el contrato de procesamiento en DataFrames para el tablero."""
    validos = pd.DataFrame(resultado.get("registros_validos") or [])
    if not validos.empty:
        validos["valor"] = pd.to_numeric(validos["valor"], errors="coerce")

    filas_invalidas = []
    for item in resultado.get("registros_invalidos") or []:
        registro = item.get("registro", {}) if isinstance(item, dict) else {}
        registro = registro if isinstance(registro, dict) else {"registro": str(registro)}
        motivos = item.get("motivos", []) if isinstance(item, dict) else []
        filas_invalidas.append({**registro, "motivos": "; ".join(map(str, motivos)), "_motivos": list(motivos)})
    invalidos = pd.DataFrame(filas_invalidas)
    if "valor" in invalidos:
        # Los valores rechazados mezclan texto y números: se muestran como texto.
        invalidos["valor"] = invalidos["valor"].map(
            lambda v: "" if v is None or (isinstance(v, float) and math.isnan(v)) else str(v)
        )

    errores = pd.DataFrame(resultado.get("errores") or [])

    # Todas las lecturas con valor numérico (válidas + rechazadas) para ver atípicos.
    lecturas = []
    if not validos.empty:
        for _, fila in validos.iterrows():
            lecturas.append({"id": fila.get("id"), "tipo": fila.get("tipo"), "valor": fila["valor"], "estado": "Válida"})
    for fila in filas_invalidas:
        numero = a_numero(fila.get("valor"))
        if numero is not None:
            tipo = fila.get("tipo")
            tipo = tipo.strip().lower() if isinstance(tipo, str) else tipo
            lecturas.append({"id": fila.get("id"), "tipo": tipo, "valor": numero, "estado": "Rechazada"})
    lecturas = pd.DataFrame(lecturas, columns=["id", "tipo", "valor", "estado"])

    for df in (validos, invalidos, errores, lecturas):
        if not df.empty:
            df.insert(0, "archivo", nombre)

    return {
        "nombre": nombre,
        "validos": validos,
        "invalidos": invalidos,
        "errores": errores,
        "lecturas": lecturas,
        "conteos": {
            "Válidos": len(validos),
            "Inválidos": len(invalidos),
            "Errores técnicos": len(errores),
        },
    }


def tipos_de(fuente):
    validos = fuente["validos"]
    if validos.empty or "tipo" not in validos:
        return []
    return [t for t in validos["tipo"].dropna().unique().tolist()]


# --------------------------------------------------------------------------
# Tablas de estadísticas
# --------------------------------------------------------------------------
def tabla_calidad(fuentes):
    filas = []
    for f in fuentes:
        c = f["conteos"]
        total = sum(c.values())
        filas.append({
            "Archivo": f["nombre"],
            "Recibidos": total,
            "Válidos": c["Válidos"],
            "Inválidos": c["Inválidos"],
            "Errores técnicos": c["Errores técnicos"],
            "% válidos": (c["Válidos"] / total * 100) if total else 0.0,
        })
    return pd.DataFrame(filas)


def tabla_estadisticas(fuentes):
    filas = []
    for f in fuentes:
        validos = f["validos"]
        for tipo in tipos_de(f):
            datos = validos[validos["tipo"] == tipo]
            serie = datos["valor"].dropna()
            if serie.empty:
                continue
            todas = f["lecturas"]
            todas = todas[todas["tipo"] == tipo]["valor"] if not todas.empty else serie
            minimo_iqr, maximo_iqr = limites_iqr(todas)
            atipicos = int(((todas < minimo_iqr) | (todas > maximo_iqr)).sum())
            unidad = datos["unidad"].mode().iat[0] if "unidad" in datos and not datos["unidad"].mode().empty else ""
            conteo = datos["clasificacion"].value_counts() if "clasificacion" in datos else pd.Series(dtype=int)
            n = len(serie)
            filas.append({
                "Archivo": f["nombre"],
                "Tipo": tipo,
                "Unidad": unidad,
                "n válidos": n,
                "Mínimo": serie.min(),
                "Q1": serie.quantile(0.25),
                "Mediana": serie.median(),
                "Media": serie.mean(),
                "Q3": serie.quantile(0.75),
                "Máximo": serie.max(),
                "Desv. estándar": serie.std() if n > 1 else 0.0,
                "Atípicos IQR (todas las lecturas)": atipicos,
                "% BAJO": conteo.get("BAJO", 0) / n * 100,
                "% NORMAL": conteo.get("NORMAL", 0) / n * 100,
                "% ALTO": conteo.get("ALTO", 0) / n * 100,
            })
    return pd.DataFrame(filas)


CONFIG_NUMEROS = {
    col: st.column_config.NumberColumn(format="%.2f")
    for col in ["Mínimo", "Q1", "Mediana", "Media", "Q3", "Máximo", "Desv. estándar"]
}
CONFIG_PORCENTAJES = {
    col: st.column_config.ProgressColumn(format="%.1f %%", min_value=0, max_value=100)
    for col in ["% válidos", "% BAJO", "% NORMAL", "% ALTO"]
}


# --------------------------------------------------------------------------
# Gráficos
# --------------------------------------------------------------------------
def dona(etiquetas, valores, colores, titulo, centro):
    fig = go.Figure(go.Pie(
        labels=etiquetas, values=valores, hole=0.62, sort=False, direction="clockwise",
        marker=dict(colors=colores),
        textinfo="label+percent", textposition="outside", automargin=True,
        hovertemplate="%{label}: %{value} registros (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=centro, showarrow=False, font=dict(size=16))
    fig.update_layout(title=titulo)
    return estilo(fig, alto=320, leyenda=False)


def dona_clasificacion(validos, titulo):
    conteo = validos["clasificacion"].value_counts() if "clasificacion" in validos else pd.Series(dtype=int)
    etiquetas = [c for c in ORDEN_CLASIFICACION if conteo.get(c, 0)]
    etiquetas += [c for c in conteo.index if c not in ORDEN_CLASIFICACION]
    valores = [int(conteo[c]) for c in etiquetas]
    colores = [COLOR_CLASIFICACION.get(c, COLOR_SENSOR_OTRO) for c in etiquetas]
    return dona(etiquetas, valores, colores, titulo, f"{sum(valores)}<br>válidos")


def dona_calidad(conteos, titulo):
    etiquetas = [e for e in ORDEN_ESTADO if conteos.get(e, 0)]
    valores = [conteos[e] for e in etiquetas]
    return dona(etiquetas, valores, [COLOR_ESTADO[e] for e in etiquetas], titulo, f"{sum(valores)}<br>recibidos")


def caja_lecturas(lecturas, validos, tipo, titulo, escala_completa=False):
    """Caja y bigotes: lecturas válidas frente a todas las lecturas numéricas.

    Los valores centinela (p. ej. 999) aplastan las cajas; por eso, salvo que se
    pida la escala completa, el eje se recorta a 3·IQR (atípicos extremos) y se
    anota cuántas lecturas quedan fuera de la vista.
    """
    fig = go.Figure()
    v = validos[validos["tipo"] == tipo]
    todas = lecturas[lecturas["tipo"] == tipo] if not lecturas.empty else lecturas
    fig.add_trace(go.Box(
        y=v["valor"], name="Válidas", text=v.get("id"),
        marker=dict(color=color_sensor(tipo), size=7), line=dict(width=1.5),
        boxpoints="outliers", boxmean=True,
        hovertemplate="%{text}<br>%{y}<extra>Válidas</extra>",
    ))
    if not todas.empty:
        fig.add_trace(go.Box(
            y=todas["valor"], name="Todas (incl. rechazadas)",
            text=todas["id"].astype(str) + " · " + todas["estado"],
            marker=dict(color=COLOR_RECHAZADAS, size=7), line=dict(width=1.5),
            boxpoints="outliers", boxmean=True,
            hovertemplate="%{text}<br>%{y}<extra>Todas</extra>",
        ))
    fig.update_layout(title=titulo)

    serie = todas["valor"] if not todas.empty else v["valor"]
    if not escala_completa and len(serie) > 3:
        q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
        bajo = max(serie.min(), q1 - 3 * (q3 - q1))
        alto = min(serie.max(), q3 + 3 * (q3 - q1))
        margen = (alto - bajo) * 0.06 or 1
        fuera_arriba, fuera_abajo = serie[serie > alto], serie[serie < bajo]
        if len(fuera_arriba) or len(fuera_abajo):
            fig.update_yaxes(range=[bajo - margen, alto + margen])
            notas = []
            if len(fuera_arriba):
                notas.append(f"▲ {len(fuera_arriba)} fuera de escala (máx. {fuera_arriba.max():g})")
            if len(fuera_abajo):
                notas.append(f"▼ {len(fuera_abajo)} fuera de escala (mín. {fuera_abajo.min():g})")
            fig.add_annotation(
                text=" · ".join(notas), xref="paper", yref="paper", x=1, y=1.02,
                xanchor="right", yanchor="bottom", showarrow=False, font=dict(size=11),
            )
    return estilo(fig, alto=380, leyenda=False)


def histograma(validos, tipo, unidad):
    datos = validos[validos["tipo"] == tipo]
    fig = px.histogram(
        datos, x="valor", color="clasificacion", nbins=30,
        category_orders={"clasificacion": ORDEN_CLASIFICACION},
        color_discrete_map=COLOR_CLASIFICACION,
        title=f"Distribución de valores válidos ({unidad})",
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(bargap=0.05, yaxis_title="Registros")
    return estilo(fig, alto=380)


def serie_temporal(validos, tipo):
    datos = validos[validos["tipo"] == tipo].copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"], errors="coerce")
    datos = datos.dropna(subset=["fecha"]).sort_values("fecha")
    if datos.empty:
        return None
    fig = px.scatter(
        datos, x="fecha", y="valor", color="clasificacion",
        category_orders={"clasificacion": ORDEN_CLASIFICACION},
        color_discrete_map=COLOR_CLASIFICACION, hover_data=["id"],
        title="Lecturas válidas en el tiempo",
    )
    fig.update_traces(marker=dict(size=7, opacity=0.8))
    return estilo(fig, alto=340)


def barras_horizontales(conteo, titulo, color):
    datos = conteo.sort_values().reset_index()
    datos.columns = ["concepto", "cantidad"]
    fig = px.bar(datos, x="cantidad", y="concepto", orientation="h", text="cantidad", title=titulo)
    fig.update_traces(marker_color=color, textposition="outside", cliponaxis=False)
    fig.update_yaxes(title=None, gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showticklabels=False)
    return estilo(fig, alto=max(220, 60 + 42 * len(datos)), leyenda=False)


def barras_apiladas_100(tabla, columnas, colores, titulo):
    largo = tabla.melt(id_vars="Archivo", value_vars=columnas, var_name="Categoría", value_name="Cantidad")
    totales = largo.groupby("Archivo")["Cantidad"].transform("sum")
    largo["Porcentaje"] = (largo["Cantidad"] / totales.where(totales > 0, 1) * 100).round(1)
    fig = px.bar(
        largo, x="Porcentaje", y="Archivo", color="Categoría", orientation="h",
        category_orders={"Categoría": columnas}, color_discrete_map=colores,
        text=largo["Porcentaje"].map(lambda p: f"{p:.0f} %" if p >= 5 else ""),
        custom_data=["Cantidad"], title=titulo,
    )
    fig.update_traces(
        marker_line_width=2, marker_line_color="rgba(255,255,255,0.9)",
        hovertemplate="%{y} · %{fullData.name}: %{customdata[0]} (%{x:.1f} %)<extra></extra>",
    )
    fig.update_layout(barcornerradius=0, xaxis=dict(range=[0, 100], ticksuffix=" %"))
    fig.update_yaxes(title=None, gridcolor="rgba(0,0,0,0)")
    return estilo(fig, alto=max(220, 120 + 48 * len(tabla)))


# --------------------------------------------------------------------------
# Secciones del tablero
# --------------------------------------------------------------------------
def kpis(conteos, extra=None):
    total = sum(conteos.values())
    tasa = conteos["Válidos"] / total * 100 if total else 0.0
    columnas = st.columns(5 + len(extra or []))
    columnas[0].metric("Recibidos", total, border=True)
    columnas[1].metric("Válidos", conteos["Válidos"], border=True)
    columnas[2].metric("Inválidos", conteos["Inválidos"], border=True)
    columnas[3].metric("Errores técnicos", conteos["Errores técnicos"], border=True)
    columnas[4].metric("Tasa de validez", f"{tasa:.1f} %", border=True)
    for col, (etiqueta, valor) in zip(columnas[5:], extra or []):
        col.metric(etiqueta, valor, border=True)


def seccion_panorama(fuentes, fallidas):
    totales = {e: sum(f["conteos"][e] for f in fuentes) for e in ORDEN_ESTADO}
    kpis(totales, [("Archivos procesados", len(fuentes))])

    for fallida in fallidas:
        st.error(f"**{fallida['nombre']}** no pudo procesarse: {fallida['error']}")

    calidad = tabla_calidad(fuentes)
    estadisticas = tabla_estadisticas(fuentes)

    st.subheader("Calidad por archivo")
    izquierda, derecha = st.columns(2)
    with izquierda:
        mostrar(barras_apiladas_100(calidad, ORDEN_ESTADO, COLOR_ESTADO, "Composición del lote recibido"))
    with derecha:
        st.dataframe(calidad, hide_index=True, width="stretch", column_config=CONFIG_PORCENTAJES)

    st.subheader("Clasificación de registros válidos")
    if not estadisticas.empty:
        por_fuente = []
        for f in fuentes:
            if f["validos"].empty or "clasificacion" not in f["validos"]:
                continue
            conteo = f["validos"]["clasificacion"].value_counts()
            por_fuente.append({"Archivo": f["nombre"], **{c: int(conteo.get(c, 0)) for c in ORDEN_CLASIFICACION}})
        columnas = st.columns(max(1, min(len(por_fuente), 3)))
        for i, f in enumerate([f for f in fuentes if not f["validos"].empty]):
            with columnas[i % len(columnas)]:
                mostrar(dona_clasificacion(f["validos"], f["nombre"]))
        if len(por_fuente) > 1:
            mostrar(barras_apiladas_100(
                pd.DataFrame(por_fuente), ORDEN_CLASIFICACION, COLOR_CLASIFICACION,
                "Comparación de la clasificación entre archivos",
            ))

        st.subheader("Valores atípicos: cajas y bigotes")
        st.caption(
            "En cada gráfico, la caja de color resume las lecturas **válidas** y la gris **todas** las "
            "lecturas numéricas (incluidas las rechazadas). La línea punteada es la media; los puntos "
            "sueltos son atípicos según el criterio IQR (fuera de Q1 − 1,5·IQR o Q3 + 1,5·IQR). "
            "Cada sensor tiene su propia escala."
        )
        pares = [(f, t) for f in fuentes for t in tipos_de(f)]
        columnas = st.columns(max(1, min(len(pares), 3)))
        for i, (f, tipo) in enumerate(pares):
            with columnas[i % len(columnas)]:
                titulo = f"{f['nombre']} · {tipo}" if len(tipos_de(f)) > 1 else f["nombre"]
                mostrar(caja_lecturas(f["lecturas"], f["validos"], tipo, titulo, escala_completa))

        st.subheader("Estadísticas descriptivas (registros válidos)")
        st.dataframe(
            estadisticas, hide_index=True, width="stretch",
            column_config={**CONFIG_NUMEROS, **CONFIG_PORCENTAJES},
        )
    else:
        st.info("No hay registros válidos para calcular indicadores.")


def seccion_fuente(fuente):
    validos, invalidos, errores, lecturas = (
        fuente["validos"], fuente["invalidos"], fuente["errores"], fuente["lecturas"]
    )
    extra = []
    if not validos.empty:
        extra = [("Media válidos", f"{validos['valor'].mean():.2f}"), ("Desv. estándar", f"{validos['valor'].std():.2f}")]
    kpis(fuente["conteos"], extra)

    izquierda, derecha = st.columns(2)
    with izquierda:
        mostrar(dona_calidad(fuente["conteos"], "Calidad del lote"))
    with derecha:
        if not validos.empty and "clasificacion" in validos:
            mostrar(dona_clasificacion(validos, "Clasificación de válidos"))
        else:
            st.info("Sin registros válidos para clasificar.")

    for tipo in tipos_de(fuente):
        datos = validos[validos["tipo"] == tipo]
        unidad = datos["unidad"].mode().iat[0] if "unidad" in datos and not datos["unidad"].mode().empty else ""
        if len(tipos_de(fuente)) > 1:
            st.markdown(f"#### Sensor: {tipo}")
        izquierda, derecha = st.columns(2)
        with izquierda:
            mostrar(caja_lecturas(lecturas, validos, tipo, f"Cajas y bigotes ({unidad})", escala_completa))
        with derecha:
            mostrar(histograma(validos, tipo, unidad))
        if "fecha" in validos:
            fig = serie_temporal(validos, tipo)
            if fig is not None:
                mostrar(fig)
    if tipos_de(fuente):
        st.caption(
            "Comparar la caja **Válidas** con **Todas** muestra cuánto distorsionarían los valores "
            "rechazados las estadísticas si no se validaran."
        )

    izquierda, derecha = st.columns(2)
    with izquierda:
        if not invalidos.empty:
            motivos = pd.Series([resumir_motivo(m) for lista in invalidos["_motivos"] for m in lista])
            mostrar(barras_horizontales(motivos.value_counts(), "Motivos de rechazo", COLOR_ESTADO["Inválidos"]))
        else:
            st.success("No se encontraron registros inválidos.")
    with derecha:
        if not errores.empty and "categoria" in errores:
            mostrar(barras_horizontales(
                errores["categoria"].value_counts(), "Errores técnicos por categoría", COLOR_ESTADO["Errores técnicos"]
            ))
        else:
            st.success("No se registraron errores técnicos.")

    nombre = Path(fuente["nombre"]).stem
    with st.expander(f"Registros válidos ({len(validos)})"):
        st.dataframe(para_mostrar(validos), hide_index=True, width="stretch")
        if not validos.empty:
            st.download_button("Descargar válidos CSV", csv_bytes(para_mostrar(validos)),
                               f"{nombre}_validos.csv", "text/csv", key=f"v_{fuente['nombre']}")
    with st.expander(f"Registros inválidos ({len(invalidos)})"):
        st.dataframe(para_mostrar(invalidos), hide_index=True, width="stretch")
        if not invalidos.empty:
            st.download_button("Descargar inválidos CSV", csv_bytes(para_mostrar(invalidos)),
                               f"{nombre}_invalidos.csv", "text/csv", key=f"i_{fuente['nombre']}")
    with st.expander(f"Errores técnicos ({len(errores)})"):
        st.dataframe(errores, hide_index=True, width="stretch")
        if not errores.empty:
            st.download_button("Descargar errores CSV", csv_bytes(errores),
                               f"{nombre}_errores.csv", "text/csv", key=f"e_{fuente['nombre']}")


def reporte_excel(fuentes):
    buffer = io.BytesIO()
    concatenar = lambda clave: pd.concat(
        [para_mostrar(f[clave]) for f in fuentes if not f[clave].empty], ignore_index=True
    ) if any(not f[clave].empty for f in fuentes) else pd.DataFrame()
    with pd.ExcelWriter(buffer, engine="openpyxl") as escritor:
        tabla_calidad(fuentes).to_excel(escritor, sheet_name="Calidad", index=False)
        tabla_estadisticas(fuentes).to_excel(escritor, sheet_name="Estadisticas", index=False)
        for clave, hoja in [("validos", "Validos"), ("invalidos", "Invalidos"), ("errores", "Errores")]:
            datos = concatenar(clave)
            datos.to_excel(escritor, sheet_name=hoja, index=False)
    return buffer.getvalue()


def seccion_reporte(fuentes):
    st.subheader("Reporte consolidado")
    st.write(
        "Libro de Excel con las hojas **Calidad**, **Estadísticas**, **Válidos**, **Inválidos** y "
        "**Errores**, que reúne todos los archivos procesados."
    )
    try:
        st.download_button(
            "Descargar reporte Excel", reporte_excel(fuentes), "datalab_reporte.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary",
        )
    except Exception as exc:
        st.warning(f"No fue posible generar el Excel: {exc}")
    todos_errores = [f["errores"] for f in fuentes if not f["errores"].empty]
    if todos_errores:
        st.markdown("#### Errores técnicos de todos los archivos")
        st.dataframe(pd.concat(todos_errores, ignore_index=True), hide_index=True, width="stretch")


# --------------------------------------------------------------------------
# Aplicación
# --------------------------------------------------------------------------
st.set_page_config(page_title="DataLab | Sensores", page_icon="📊", layout="wide")
st.title("DataLab — Procesamiento y análisis de sensores")
st.caption("Aplicación integradora: calidad, robustez y múltiples fuentes de datos.")

with st.sidebar:
    st.header("Fuente de datos")
    modo = st.radio("Selecciona el modo", ["Carga de archivos", "Demostración en memoria"])
    archivos, usar_ejemplos = [], False
    if modo == "Carga de archivos":
        archivos = st.file_uploader(
            "Selecciona uno o varios archivos CSV, JSON o Excel",
            type=EXTENSIONES, accept_multiple_files=True,
        ) or []
        ejemplos = sorted(p for p in CARPETA_EJEMPLOS.glob("*") if p.suffix.lstrip(".").lower() in EXTENSIONES)
        if ejemplos:
            usar_ejemplos = st.toggle(
                "Usar datasets de ejemplo", value=False,
                help="Carga " + ", ".join(p.name for p in ejemplos) + " desde data/raw.",
            )
    st.divider()
    st.header("Visualización")
    escala_completa = st.toggle(
        "Escala completa en cajas y bigotes", value=False,
        help="Incluye valores extremos (por ejemplo, centinelas como 999) aunque compriman las cajas.",
    )
    st.caption(
        "Las categorías BAJO/NORMAL/ALTO son reglas pedagógicas para datos sintéticos. "
        "Los atípicos IQR son una referencia estadística, no un criterio de validación."
    )

procesadas = []
if modo == "Demostración en memoria":
    try:
        procesadas.append({"nombre": "Demostración en memoria", "resultado": ejecutar_demo()})
    except Exception as exc:
        procesadas.append({"nombre": "Demostración en memoria", "error": f"{type(exc).__name__}: {exc}"})
else:
    entradas = {}
    if usar_ejemplos:
        for ruta in ejemplos:
            entradas[ruta.name] = ruta.read_bytes()
    for archivo in archivos:  # Un archivo subido reemplaza al ejemplo con el mismo nombre.
        entradas[archivo.name] = archivo.getvalue()
    procesadas = [procesar_fuente(nombre, contenido) for nombre, contenido in entradas.items()]

if not procesadas:
    st.info(
        "Sube uno o varios archivos (por ejemplo, **temperatura.csv**, **presion.json** y "
        "**humedad.xlsx**) desde la barra lateral, o activa **Usar datasets de ejemplo**."
    )
    st.stop()

fallidas = [p for p in procesadas if "error" in p]
fuentes = [construir_marcos(p["nombre"], p["resultado"]) for p in procesadas if "resultado" in p]

if not fuentes:
    for fallida in fallidas:
        st.error(f"**{fallida['nombre']}** no pudo procesarse: {fallida['error']}")
    st.stop()

pestanas = st.tabs(["Panorama general"] + [f"📄 {f['nombre']}" for f in fuentes] + ["Reporte"])
with pestanas[0]:
    seccion_panorama(fuentes, fallidas)
for pestana, fuente in zip(pestanas[1:-1], fuentes):
    with pestana:
        seccion_fuente(fuente)
with pestanas[-1]:
    seccion_reporte(fuentes)
