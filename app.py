import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from math import *

st.set_page_config(page_title="Preparación de Productos Químicos", layout="centered")

st.markdown(
    """
    <h1 style='text-align: center;'>Preparación de Productos Químicos Complejo Hidrotratamiento</h1>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def cargar_datos():
    df = pd.read_excel("plantilla_recetas_productos.xlsx", sheet_name="Sheet1")
    df.columns = df.columns.str.strip()
    return df

df = cargar_datos()

# --- Selección de unidad y producto ---
unidades = sorted(df["Unidad"].unique())
unidad_seleccionada = st.selectbox("Selecciona la unidad", unidades)

productos_filtrados = df[df["Unidad"] == unidad_seleccionada]
productos = sorted(productos_filtrados["Nombre_comercial"].unique())
producto_seleccionado = st.selectbox("Selecciona el producto químico", productos)

datos = productos_filtrados[productos_filtrados["Nombre_comercial"] == producto_seleccionado].iloc[0]

# --- Entradas del usuario ---
densidad_solvente_input = st.number_input(
    f"Densidad de solvente [kg/m³]", value=float(datos["Densidad_Solvente_Referencia"]))
nivel_inicial = st.number_input("Nivel inicial del tanque [%]", min_value=0.0, max_value=100.0, value=10.0)
nivel_final = st.number_input("Nivel final del tanque [%]", min_value=0.0, max_value=100.0, value=50.0)

# --- Cálculo ---
def calcular_volumen(nivel, ecuacion):
    x = nivel
    return eval(ecuacion)

if st.button("Calcular preparación"):
    ecuacion = datos["Ecuacion_Volumen"]
    densidad_soluto = datos["Densidad_Soluto"]
    concentracion = datos["Concentracion_Porcentual"] / 100.0
    nombre_comercial = datos["Nombre_comercial"]

    volumen_i = calcular_volumen(nivel_inicial, ecuacion)
    volumen_f = calcular_volumen(nivel_final, ecuacion)
    volumen_objetivo = volumen_f - volumen_i

    masa_base = 100.0
    masa_soluto_base = masa_base * concentracion
    masa_solvente_base = masa_base - masa_soluto_base

    vol_soluto_base = masa_soluto_base / densidad_soluto
    vol_solvente_base = masa_solvente_base / densidad_solvente_input
    volumen_total_base = vol_soluto_base + vol_solvente_base
    densidad_real = masa_base / volumen_total_base

    masa_total = volumen_objetivo * densidad_real
    masa_soluto = masa_total * concentracion
    masa_solvente = masa_total - masa_soluto

    volumen_soluto = masa_soluto / densidad_soluto
    volumen_solvente = masa_solvente / densidad_solvente_input

    # --- Mostrar resultados ---
    st.subheader("📊 Resultados técnicos")
    resultados = {
        "Volumen objetivo (m³)": round(volumen_objetivo, 4),
        "Densidad solución (kg/m³)": round(densidad_real, 2),
        "Masa total solución (kg)": round(masa_total, 2),
        f"Masa {nombre_comercial} (kg)": round(masa_soluto, 2),
        "Masa solvente (kg)": round(masa_solvente, 2),
        f"Volumen {nombre_comercial} (m³)": round(volumen_soluto, 4),
        "Volumen solvente (m³)": round(volumen_solvente, 4),
        "Volumen total verificado (m³)": round(volumen_soluto + volumen_solvente, 4)
    }
    st.json(resultados)

    # --- Generar texto para correo ---
    zona_peru = pytz.timezone("America/Lima")
    fecha_hoy = datetime.now(zona_peru).strftime("%Y-%m-%d")

    texto = f"""
1.         Premisas para la preparación:

a. Densidad del solvente: {densidad_solvente_input:.1f} kg/m³ (Data JLBT: {fecha_hoy}).
b. Nivel inicial: {nivel_inicial:.1f} %
c. Nivel final: {nivel_final:.1f} %

2.         Preparación de la solución:

- {nombre_comercial} (soluto): {int(round(volumen_soluto*1000))} L – {int(round(masa_soluto))} kg
- {datos['Solvente']} (solvente): {int(round(volumen_solvente*1000))} L – {int(round(masa_solvente))} kg
- Total solución preparada: {int(round(volumen_objetivo*1000))} L – {int(round(masa_total))} kg

3.         Información logística:

- Código material: {datos['Codigo']}
- Proveedor: {datos['Proveedor']}
- Presentación: {datos['Presentacion']}
"""

    st.subheader("✉️ Texto técnico para reporte o correo")
    st.caption("Puedes copiar o descargar el texto generado.")

    # Área de texto editable (opcional)
    st.text_area("Texto generado (puedes copiar manualmente):", value=texto.strip(), height=300)

    # Botón copiar con JavaScript funcional
    components.html(f"""
        <script>
            function copiarTexto() {{
                var texto = `{texto.strip().replace("`", "\\`")}`;
                navigator.clipboard.writeText(texto).then(function() {{
                    alert('Texto copiado al portapapeles');
                }});
            }}
        </script>
        <button onclick="copiarTexto()"
                style="background-color: #2563eb; color: white; padding: 8px 16px;
                       border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
            📋 Copiar
        </button>
    """, height=50)

    # Botón para descarga
    st.download_button(
        label="📄 Descargar texto como .txt",
        data=texto,
        file_name=f"reporte_preparacion_{unidad_seleccionada}_{nombre_comercial}.txt",
        mime="text/plain"
    )

# Pie de página personalizado
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 14px;'>
        ✳ Creado por <strong>Denis Sánchez</strong> – Refinería Talara, 2025
    </div>
    """,
    unsafe_allow_html=True
)
