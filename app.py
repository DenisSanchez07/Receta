import streamlit as st
import pandas as pd
import numpy as np
from math import pi
from datetime import date

# --- Cargar datos Excel y limpiar encabezados ---
@st.cache_data
def cargar_datos():
    df = pd.read_excel("plantilla_recetas_productos.xlsx")
    df.columns = df.columns.str.strip()  # Limpiar nombres de columnas
    df["Codigo"] = df["Codigo"].astype(str).str.strip()  # Asegurar sin espacios
    df["Nombre_comercial"] = df["Nombre_comercial"].astype(str).str.strip()
    df["Unidad"] = df["Unidad"].astype(str).str.strip()
    return df

# --- Función para calcular volumen desde ecuación nivel ---
def calcular_volumen(ecuacion, x):
    try:
        return eval(ecuacion.replace("x", str(x)).replace("^", "**"))
    except:
        return 0

# --- Título principal ---
st.title("📘 Preparación de Soluciones Químicas")

# --- Cargar plantilla ---
df = cargar_datos()

# --- Selección de unidad ---
unidad_sel = st.selectbox("Selecciona la unidad:", sorted(df["Unidad"].unique()))
productos_disponibles = df[df["Unidad"] == unidad_sel]["Nombre_comercial"].unique()
producto_sel = st.selectbox("Selecciona el producto químico:", sorted(productos_disponibles))

# --- Filtrado del DataFrame ---
data = df[(df["Unidad"] == unidad_sel) & (df["Nombre_comercial"] == producto_sel)].reset_index(drop=True)

if not data.empty:
    # Extraer valores únicos
    tipo = data["Tipo_Producto"].values[0]
    concentracion = data["Concentracion_Porcentual"].values[0]
    densidad_soluto = data["Densidad_Soluto"].values[0]
    densidad_ref = data["Densidad_Solvente_Referencia"].values[0]
    ecuacion = data["Ecuacion_Volumen"].values[0]
    codigo = data["Codigo"].values[0]
    proveedor = data["Proveedor"].values[0]
    presentacion = data["Presentacion"].values[0]

    st.markdown("### Parámetros de Preparación")

    densidad_solvente = st.number_input("Ingrese la densidad actual del solvente (kg/m³):", value=densidad_ref)
    nivel_inicial = st.number_input("Nivel inicial (%):", value=15.0)
    nivel_final = st.number_input("Nivel final (%):", value=88.0)

    # Calcular volumen a preparar
    volumen_total = calcular_volumen(ecuacion, nivel_final) - calcular_volumen(ecuacion, nivel_inicial)
    masa_total = volumen_total * ((concentracion / 100) * densidad_soluto + (1 - (concentracion / 100)) * densidad_solvente)

    masa_soluto = (concentracion / 100) * masa_total
    masa_solvente = masa_total - masa_soluto
    volumen_soluto = masa_soluto / densidad_soluto
    volumen_solvente = masa_solvente / densidad_solvente

    # --- Resultados ---
    st.markdown("### Resultados de Preparación")
    st.dataframe(pd.DataFrame({
        "Componente": ["Soluto", "Solvente", "Total"],
        "Volumen (L)": [round(volumen_soluto, 2), round(volumen_solvente, 2), round(volumen_total, 2)],
        "Masa (kg)": [round(masa_soluto, 2), round(masa_solvente, 2), round(masa_total, 2)]
    }))

    # --- Texto para el correo ---
    st.markdown("### Generación de Texto para Comunicación")
    texto = f"""
1. **Premisas para la preparación:**

   a. Densidad de la {tipo.lower()}: {densidad_solvente:.1f} kg/m³ (Dato {date.today()}).

   b. Nivel del drum {unidad_sel}-D-025 a considerar: {nivel_inicial:.1f} %.

   c. Objetivo para aforar es hasta el {nivel_final:.1f}% del nivel, para utilizar la máxima cantidad del producto químico una vez abierto el cilindro, que sea fácil de contabilizar en campo y estar por debajo de la alarma de alta (90%).

2. **Preparación de la Solución:**

   a. Volumen para usar de {producto_sel}:\n      {round(volumen_soluto, 0)} L ({round(masa_soluto, 0)} kg)

   b. Volumen para usar de {tipo.lower()}:\n      {round(volumen_solvente, 0)} L ({round(masa_solvente, 0)} kg)

   c. Volumen total de solución:\n      {round(volumen_total, 0)} L ({round(masa_total, 0)} kg)

3. **Información para retirar producto de almacén (JIYA):**

   a. Código Material: {codigo}

   b. Proveedor: {proveedor}

   c. Nombre comercial: {producto_sel}

   d. Presentación: {presentacion}
    """
    st.code(texto, language="markdown")

# --- Pie de autor ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 14px;'>
    ✦ Creado por <strong>Denis Sánchez</strong> – Refinería Talara, 2025
    </div>
    """,
    unsafe_allow_html=True
)
