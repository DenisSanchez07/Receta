import streamlit as st
import pandas as pd
import numpy as np

# Cargar datos desde Excel
@st.cache_data
def cargar_datos():
    return pd.read_excel("plantilla_recetas_productos.xlsx")

def evaluar_volumen(nivel, ecuacion_str, porcentaje=True):
    x = nivel / 100 if porcentaje else nivel
    try:
        return eval(ecuacion_str)
    except:
        return np.nan

def main():
    st.title("📘 Preparación de Soluciones Químicas")

    df = cargar_datos()

    # Selección de unidad y tipo de producto
    unidad_seleccionada = st.selectbox("Selecciona la unidad:", df["Unidad"].unique())

    tipos_disponibles = df[df["Unidad"] == unidad_seleccionada]["Tipo_Producto"].unique()
    tipo_producto = st.selectbox("Selecciona el tipo de producto:", tipos_disponibles)

    # Filtro del producto seleccionado
    data = df[(df["Unidad"] == unidad_seleccionada) & (df["Tipo_Producto"] == tipo_producto)].iloc[0]

    st.subheader("Parámetros de Preparación")
    densidad_solvente_actual = st.number_input("Ingrese la densidad actual del solvente (kg/m³):", value=729.8)
    nivel_inicial = st.number_input("Nivel inicial (%):", value=15.0)
    nivel_final = st.number_input("Nivel final (%):", value=88.0)

    # Evaluar volumen total en litros con ecuación
    volumen_total = evaluar_volumen(nivel_final, data["Ecuacion_Volumen"], porcentaje=True)

    # Concentración en fracción
    concentracion = data["Concentracion_Porcentual"] / 100

    # Volumen soluto y solvente en litros
    volumen_soluto = volumen_total * concentracion
    volumen_solvente = volumen_total - volumen_soluto

    # Masas en kg
    masa_soluto = volumen_soluto * data["Densidad_Soluto"]
    masa_solvente = volumen_solvente * densidad_solvente_actual

    st.subheader("Resultados de Preparación")
    resultados = pd.DataFrame({
        "Componente": ["Soluto", "Solvente", "Total"],
        "Volumen (L)": [round(volumen_soluto, 2), round(volumen_solvente, 2), round(volumen_total, 2)],
        "Masa (kg)": [round(masa_soluto, 2), round(masa_solvente, 2), round(masa_soluto + masa_solvente, 2)]
    })
    st.dataframe(resultados, use_container_width=True)

if __name__ == "__main__":
    main()
