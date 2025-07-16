import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Cargar datos desde Excel (asegúrate de que el archivo se haya subido y esté en el mismo directorio)
@st.cache_data
def cargar_datos():
    return pd.read_excel("plantilla_recetas_productos.xlsx")
st.write(df.columns.tolist())


def evaluar_volumen(nivel, ecuacion_str, porcentaje=True):
    x = nivel / 100 if porcentaje else nivel
    try:
        return eval(ecuacion_str)
    except:
        return np.nan

def calcular_densidad_real(soluto_kg, soluto_volumen_l, densidad_solvente):
    masa_soluto = soluto_kg
    volumen_soluto = soluto_volumen_l
    volumen_total_m3 = (volumen_soluto / 1000) + (masa_soluto / densidad_solvente)
    return masa_soluto / volumen_total_m3

def main():
    st.title("📃 Preparación de Soluciones Químicas")

    df = cargar_datos()

    # Selección de unidad y producto
    unidades = df["Unidad"].dropna().unique()
    unidad_seleccionada = st.selectbox("Selecciona la unidad:", unidades)

    productos = df[df["Unidad"] == unidad_seleccionada]["Producto químico"].unique()
    producto_seleccionado = st.selectbox("Selecciona el producto químico:", productos)

    data = df[(df["Unidad"] == unidad_seleccionada) & (df["Producto químico"] == producto_seleccionado)].iloc[0]

    # Ingreso de parámetros
    st.subheader("Parámetros de Preparación")
    densidad_solvente = st.number_input("Ingrese la densidad actual del solvente (kg/m³):", value=729.8, step=0.01)
    nivel_inicial = st.number_input("Nivel inicial (%):", value=15.0)
    nivel_final = st.number_input("Nivel final (%):", value=88.0)

    # Cálculo de volumen y masas
    porcentaje = True if data["Tipo_Ecuacion"] == "porcentaje" else False

    volumen_total = evaluar_volumen(nivel_final, data["Ecuacion_Litros"], porcentaje) - evaluar_volumen(nivel_inicial, data["Ecuacion_Litros"], porcentaje)
    volumen_soluto = data["Volumen Soluto (L)"]
    masa_soluto = data["Masa Soluto (kg)"]
    volumen_solvente = volumen_total - volumen_soluto
    masa_solvente = volumen_solvente * densidad_solvente / 1000
    masa_total = masa_soluto + masa_solvente

    # Mostrar tabla de resultados
    st.subheader("Resultados de Preparación")
    resultados = pd.DataFrame({
        "Componente": ["Soluto", "Solvente", "Total"],
        "Volumen (L)": [round(volumen_soluto, 2), round(volumen_solvente, 2), round(volumen_total, 2)],
        "Masa (kg)": [round(masa_soluto, 2), round(masa_solvente, 2), round(masa_total, 2)]
    })
    st.dataframe(resultados)

    # Texto para correo o reporte
    st.subheader("Texto para Comunicación Técnica")
    texto_correo = f"""
    1.   Premisas para la preparación:
    a. Densidad de la {data['Nombre Solvente'].lower()}: {densidad_solvente:.1f} kg/m³ (Data JLBT {datetime.today().date()}).
    b. Nivel del {data['Tambor']}: {nivel_inicial:.1f} %.
    c. Objetivo para aforar es hasta el {nivel_final:.1f} %, para utilizar la máxima cantidad del PQ una vez abierto el cilindro, que sea fácil de contabilizar en campo y estar por debajo de la alarma de alta ({data['Alarma_Alta_Texto']}).

    2.   Preparación de la Solución:
    | Componente           | Volumen     | Masa     |
    |----------------------|-------------|----------|
    | {data['Producto químico']} (soluto)   | {volumen_soluto:.2f} L   | {masa_soluto:.2f} kg |
    | {data['Nombre Solvente']}     | {volumen_solvente:.2f} L   | {masa_solvente:.2f} kg |
    | Total solución preparada | {volumen_total:.2f} L   | {masa_total:.2f} kg |
    """
    st.code(texto_correo, language="markdown")

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 14px;'>
            ✳ Creado por <strong>Denis Sánchez</strong> – Refinería Talara, 2025
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
