import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

# Función para cargar datos del Excel
@st.cache_data
def cargar_datos():
    return pd.read_excel("plantilla_recetas_productos.xlsx")

# Función para evaluar la ecuación
def evaluar_volumen(x, ecuacion):
    try:
        return eval(ecuacion.replace("x", str(x / 100)))
    except Exception as e:
        st.error(f"Error en la fórmula: {e}")
        return np.nan

# Cargar datos
data = cargar_datos()

# Título principal
st.title("📘 Preparación de Soluciones Químicas")

# Selección de unidad
unidad_seleccionada = st.selectbox("Selecciona la unidad:", sorted(data["Unidad"].dropna().unique()))
productos_disponibles = data[data["Unidad"] == unidad_seleccionada]["Nombre_comercial"].dropna().unique()
producto_seleccionado = st.selectbox("Selecciona el producto químico:", sorted(productos_disponibles))

# Filtrar datos del producto
datos_producto = data[(data["Unidad"] == unidad_seleccionada) & (data["Nombre_comercial"] == producto_seleccionado)].iloc[0]

# Entrada de parámetros
st.subheader("Parámetros de Preparación")
densidad_solvente = st.number_input("Ingrese la densidad actual del solvente (kg/m³):", value=float(datos_producto["Densidad_Solvente_Referencia"]), step=0.01)
nivel_inicial = st.number_input("Nivel inicial (%):", min_value=0.0, max_value=100.0, value=15.0, step=0.1)
nivel_final = st.number_input("Nivel final (%):", min_value=0.0, max_value=100.0, value=88.0, step=0.1)

# Evaluación del volumen a preparar
volumen_total = evaluar_volumen(nivel_final, datos_producto["Ecuacion_Volumen"]) - evaluar_volumen(nivel_inicial, datos_producto["Ecuacion_Volumen"])
volumen_total = round(volumen_total, 2)

# Cálculo de volúmenes y masas
porc_soluto = datos_producto["Concentracion_Porcentual"] / 100
volumen_soluto = round(porc_soluto * volumen_total, 2)
volumen_solvente = round(volumen_total - volumen_soluto, 2)

masa_soluto = round(volumen_soluto * datos_producto["Densidad_Soluto"], 2)
masa_solvente = round(volumen_solvente * densidad_solvente, 2)
masa_total = round(masa_soluto + masa_solvente, 2)

# Mostrar tabla de resultados
st.subheader("Resultados de Preparación")
df_resultados = pd.DataFrame({
    "Componente": ["Soluto", "Solvente", "Total"],
    "Volumen (L)": [volumen_soluto, volumen_solvente, volumen_total],
    "Masa (kg)": [masa_soluto, masa_solvente, masa_total]
})
st.dataframe(df_resultados, use_container_width=True)

# Generar texto tipo correo
st.subheader("Texto para Comunicación Técnica")

fecha_actual = datetime.today().strftime("%Y-%m-%d")
texto_correo = f"""
1.         Premisas para la preparación:

a. Densidad de la nafta pesada hidrotratada: {densidad_solvente} kg/m³ (Data JLBT {fecha_actual}).
b. Nivel del drum {datos_producto['Tanque_preparacion']} a considerar: {nivel_inicial} %.
c. Objetivo para aforar es hasta el {nivel_final}%, para utilizar la máxima cantidad del PQ una vez abierto el cilindro, 
   que sea fácil de contabilizar en campo y estar por debajo de la alarma de alta ({datos_producto['Alarma_Alta']}%).

2.         Preparación de la Solución:

| Componente              | Volumen     | Masa     |
|-------------------------|-------------|----------|
| {producto_seleccionado} (soluto)     | {volumen_soluto} L     | {masa_soluto} kg |
| Nafta pesada hidrotratada          | {volumen_solvente} L     | {masa_solvente} kg |
| Total solución preparada           | {volumen_total} L     | {masa_total} kg |

3.         Información para retirar producto de almacén (JIYA):

a. Código Material: {datos_producto['Codigo']}.
b. Proveedor: {datos_producto['Proveedor']}.
c. Nombre comercial: {producto_seleccionado}.
d. Presentación: {datos_producto['Presentacion']}.
"""

st.code(texto_correo, language="markdown")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 14px;'>
        📌 Creado por <strong>Denis Sánchez</strong> – Refinería Talara, 2025
    </div>
    """,
    unsafe_allow_html=True
)
