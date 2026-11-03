"""Interfaz Streamlit provista por el docente.

La interfaz está completa en su capa gráfica desde el día uno.
El modo de demostración usa los registros en memoria. La carga real de archivos
se habilita cuando el rol C complete lectores.py y el rol B integre errores.
No colocar reglas de negocio en este archivo.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from src.data.fuentes_memoria import cargar_desde_memoria
from src.processing.clasificacion import clasificar_valor

st.set_page_config(page_title="DataLab | Sensores", page_icon="📊", layout="wide")
st.title("DataLab — Procesamiento y análisis de sensores")
st.caption("Interfaz provista por el docente. La lógica de negocio reside en los módulos de src/.")

with st.sidebar:
    st.header("Fuente de datos")
    fuente = st.radio("Selecciona el modo", ["Demostración en memoria", "Carga de archivos"])
    st.info("La demostración está disponible desde la primera entrega.")
    archivo_subido = None
    if fuente == "Carga de archivos":
        st.info("La recepción del archivo está disponible desde el día uno. Su lectura e integración al procesamiento se habilitan con los módulos del rol C en semana 12.")
        archivo_subido = st.file_uploader("Selecciona un archivo", type=["csv", "json", "xlsx"])
    st.divider()
    st.caption("DataLab · Proyecto integrador")

if fuente == "Demostración en memoria":
    registros = cargar_desde_memoria()
    resultados = []
    for registro in registros:
        fila = registro.copy()
        fila["clasificacion"] = clasificar_valor(float(fila["valor"]), fila["tipo"])
        resultados.append(fila)
    df = pd.DataFrame(resultados)

    total = len(df)
    altos = int((df["clasificacion"] == "ALTO").sum())
    normales = int((df["clasificacion"] == "NORMAL").sum())
    bajos = int((df["clasificacion"] == "BAJO").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", total)
    c2.metric("BAJO", bajos)
    c3.metric("NORMAL", normales)
    c4.metric("ALTO", altos)

    tab1, tab2, tab3 = st.tabs(["Registros", "Indicadores", "Calidad"])
    with tab1:
        st.subheader("Registros procesados")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Descargar resultados CSV", df.to_csv(index=False).encode("utf-8-sig"),
                           "datalab_resultados_demo.csv", "text/csv")
    with tab2:
        st.subheader("Clasificación por sensor")
        conteo = df.groupby(["tipo", "clasificacion"]).size().reset_index(name="cantidad")
        fig = px.bar(conteo, x="tipo", y="cantidad", color="clasificacion",
                     barmode="group", text="cantidad", title="Distribución de categorías")
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Promedio por sensor")
        promedios = df.groupby("tipo", as_index=False)["valor"].mean()
        st.dataframe(promedios, use_container_width=True, hide_index=True)
    with tab3:
        st.subheader("Estado de los datos")
        st.success("Los registros de demostración están completos y utilizan valores numéricos.")
        st.write("La validación ampliada y el panel de errores se conectarán a los módulos de los estudiantes durante las semanas 10 y 11.")
else:
    st.subheader("Carga de archivos")
    if archivo_subido is not None:
        st.success(f"Archivo recibido: {archivo_subido.name}")
        st.write(f"Tamaño: {archivo_subido.size:,} bytes")
        st.write(f"Formato: {archivo_subido.name.rsplit('.', 1)[-1].upper()}")
        st.warning("La recepción gráfica funciona desde el día uno. La lectura estructurada y el procesamiento del archivo se conectarán cuando se integren los módulos del rol C (semana 12) y del rol B.")
    else:
        st.info("Selecciona un archivo CSV, JSON o Excel. La carga visual está disponible desde la primera entrega.")
    st.caption("La interfaz no interpreta ni transforma los datos: esa responsabilidad pertenece a los módulos de lectura y procesamiento.")
