import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

@st.cache_data
def cargar_datos():
    return pd.read_excel("plantilla_recetas_productos.xlsx")

def evaluar_volumen(nivel, ecuacion_str):
    try:
        x = nivel
        return eval(ecuacion_str)
    except:
        return np.nan

def calcular_resultados(volumen_litros, porcentaje, dens_soluto, dens_solvente):
    fraccion = porcentaje / 100
    vol_soluto = volumen_litros * fraccion
    vol_solvente = volumen_litros - vol_soluto
    masa_soluto = vol_soluto * dens_soluto / 1000
    masa_solvente = vol_solvente * dens_solvente / 1000
    masa_total = masa_soluto + masa_solvente

    return pd.DataFrame({
        "Componente": ["Soluto", "Solvente", "Total"],
        "Volumen (L)": [round(vol_soluto, 2), round(vol_solvente, 2), round(volumen_litros, 2)],
        "Masa (kg)": [round(masa_soluto, 2), round(masa_solvente, 2), round(masa_total, 2)]
    })

def main():
    st.title("🧪 Preparación de Soluciones Químicas por Unidad")
    df = cargar_datos()

    unidad = st.selectbox("Selecciona la unidad", df["Unidad"].unique())
    productos = df[df["Unidad"] == unidad]["Nombre_comercial"].unique()
    producto = st.selectbox("Selecciona el producto químico", productos)

    datos = df[(df["Unidad"] == unidad) & (df["Nombre_comercial"] == producto)].iloc[0]

    densidad_solvente = st.number_input("Densidad actual del solvente (kg/m³)", value=float(datos["Densidad_Solvente_Referencia"]))
    nivel_inicial = st.number_input("Nivel inicial (%)", min_value=0.0, max_value=100.0, value=15.0)
    nivel_final = st.number_input("Nivel final (%)", min_value=0.0, max_value=100.0, value=88.0)

    volumen_litros = evaluar_volumen(nivel_final, datos["Ecuacion_Volumen"]) * 1000  # m³ a L
    resultado = calcular_resultados(volumen_litros, datos["Concentracion_Porcentual"], datos["Densidad_Soluto"], densidad_solvente)

    st.subheader("📊 Resultados de Preparación")
    st.dataframe(resultado, use_container_width=True)

    st.subheader("📄 Texto Técnico para Comunicación")
    fecha_actual = datetime.today().strftime("%Y-%m-%d")
    texto = f"""
1. Premisas para la preparación:

a. Densidad del solvente utilizada: {densidad_solvente:.1f} kg/m³ (Data JLBT {fecha_actual}).
b. Nivel del recipiente {datos['Tanque_preparacion']} a considerar: {nivel_inicial:.1f} %.
c. Aforar hasta {nivel_final:.1f} % para máxima eficiencia sin superar la alarma de alta ({float(datos['Alarma_Alta'])*100:.2f}%).

d. Producto químico: {datos['Nombre_comercial']} - {datos['Tipo_Producto']}
e. Presentación: {datos['Presentacion']}, Proveedor: {datos['Proveedor']}, Código: {datos['Codigo']}

2. Preparación de la Solución:

{resultado.to_string(index=False)}
    """
    st.code(texto)

if __name__ == "__main__":
    main()
