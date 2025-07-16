import streamlit as st
import pandas as pd
import datetime
import math

# Cargar datos desde Excel (con @st.cache para que no recargue innecesariamente)
@st.cache_data
def cargar_datos():
    return pd.read_excel("plantilla_recetas_productos.xlsx")

data = cargar_datos()

st.title("📘 Preparación de Soluciones Químicas")

# --- Selección de unidad y producto químico ---
unidades = data["Unidad"].unique()
unidad_seleccionada = st.selectbox("Selecciona la unidad:", unidades)

productos = data[data["Unidad"] == unidad_seleccionada]["Producto químico"].unique()
producto_seleccionado = st.selectbox("Selecciona el producto químico:", productos)

# --- Filtro del producto seleccionado ---
data_filtro = data[(data["Unidad"] == unidad_seleccionada) & (data["Producto químico"] == producto_seleccionado)]
data = data_filtro.iloc[0]  # Solo uno

# --- Entrada de parámetros ---
st.subheader("Parámetros de Preparación")
densidad_solvente = st.number_input("Ingrese la densidad actual del solvente (kg/m³):", value=729.8, step=1.0)
nivel_inicial = st.number_input("Nivel inicial (%):", value=15.0, step=1.0)
nivel_final = st.number_input("Nivel final (%):", value=88.0, step=1.0)

# --- Cálculo del volumen total en litros ---
def calcular_volumen_total(nivel_inicial, nivel_final, ecuacion):
    x1 = nivel_inicial / 100
    x2 = nivel_final / 100
    volumen = eval(ecuacion.replace("x", "x2")) - eval(ecuacion.replace("x", "x1"))
    return volumen * 1000  # convertir a litros

volumen_total_L = calcular_volumen_total(nivel_inicial, nivel_final, data["Ecuación"])

# --- Cálculo de masa de soluto y solvente ---
concentracion = data["% Concentración"] / 100
densidad_soluto = data["Densidad soluto"]

volumen_soluto_L = volumen_total_L * concentracion
volumen_solvente_L = volumen_total_L - volumen_soluto_L

masa_soluto_kg = volumen_soluto_L * densidad_soluto / 1000
masa_solvente_kg = volumen_solvente_L * densidad_solvente / 1000
masa_total_kg = masa_soluto_kg + masa_solvente_kg

# --- Mostrar resultados ---
st.subheader("Resultados de Preparación")
df_resultados = pd.DataFrame({
    "Componente": ["Soluto", "Solvente", "Total"],
    "Volumen (L)": [volumen_soluto_L, volumen_solvente_L, volumen_total_L],
    "Masa (kg)": [masa_soluto_kg, masa_solvente_kg, masa_total_kg]
})
df_resultados = df_resultados.round(2)
st.dataframe(df_resultados, hide_index=True)

# --- Texto del correo ---
fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
nombre_solvente = data["Nombre solvente"]
codigo_equipo = data["Código equipo"]
producto = data["Producto químico"]

texto_correo = f"""
1.     Premisas para la preparación:

a. Densidad de la {nombre_solvente.lower()}: {densidad_solvente:.2f} kg/m³ (Data JLBT {fecha_actual}).
b. Nivel del drum {codigo_equipo} a considerar: {nivel_inicial:.1f} %.
c. Objetivo para aforar es hasta el {nivel_final:.1f} %, para utilizar la máxima cantidad del PQ una vez abierto el cilindro, que sea fácil de contabilizar en campo y estar por debajo de la alarma de alta (90%).

2.     Preparación de la Solución:

| Componente       | Volumen (L) | Masa (kg) |
|------------------|-------------|-----------|
| {producto} (soluto) | {df_resultados.loc[0, 'Volumen (L)']:.2f}       | {df_resultados.loc[0, 'Masa (kg)']:.2f}     |
| {nombre_solvente}   | {df_resultados.loc[1, 'Volumen (L)']:.2f}       | {df_resultados.loc[1, 'Masa (kg)']:.2f}     |
| Total solución preparada | {df_resultados.loc[2, 'Volumen (L)']:.2f}       | {df_resultados.loc[2, 'Masa (kg)']:.2f}     |
"""

st.markdown("---")
st.markdown("#### Vista previa del correo generado:")
st.code(texto_correo, language="markdown")

# --- Firma ---
st.markdown("""
<div style='text-align: center; color: gray; font-size: 14px;'>
✦ Creado por <strong>Denis Sánchez</strong> – Refinería Talara, 2025
</div>
""", unsafe_allow_html=True)
