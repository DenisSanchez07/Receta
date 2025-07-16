import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_data
def cargar_datos():
    return pd.read_excel("plantilla_recetas_productos.xlsx")

def evaluar_volumen(nivel, ecuacion, porcentaje=True):
    x = nivel / 100 if porcentaje else nivel
    return eval(ecuacion)

def main():
    st.set_page_config(page_title="Preparación de Soluciones Químicas", page_icon=":blue_book:", layout="centered")
    st.title("📘 Preparación de Soluciones Químicas")

    df = cargar_datos()

    unidades = df["Unidad"].unique()
    unidad_seleccionada = st.selectbox("Selecciona la unidad:", unidades)

    productos_disponibles = df[df["Unidad"] == unidad_seleccionada]["Nombre_comercial"]
    producto_seleccionado = st.selectbox("Selecciona el producto químico:", productos_disponibles)

    data = df[(df["Unidad"] == unidad_seleccionada) & (df["Nombre_comercial"] == producto_seleccionado)].iloc[0]

    st.subheader("Parámetros de Preparación")
    densidad_solvente = st.number_input("Ingrese la densidad actual del solvente (kg/m³):", value=729.8)
    nivel_inicial = st.number_input("Nivel inicial (%):", value=15.0)
    nivel_final = st.number_input("Nivel final (%):", value=88.0)

    volumen_total = evaluar_volumen(nivel_final, data["Ecuacion_Litros"], porcentaje=data["Tipo_Ecuacion"] == "porcentaje") - \
                    evaluar_volumen(nivel_inicial, data["Ecuacion_Litros"], porcentaje=data["Tipo_Ecuacion"] == "porcentaje")

    volumen_soluto = volumen_total * data["Concentracion_%"] / 100
    volumen_solvente = volumen_total - volumen_soluto

    masa_soluto = volumen_soluto * data["Densidad_soluto"]
    masa_solvente = volumen_solvente * densidad_solvente
    masa_total = masa_soluto + masa_solvente

    st.subheader("Resultados de Preparación")
    resultados = pd.DataFrame({
        "Componente": ["Soluto", "Solvente", "Total"],
        "Volumen (L)": [round(volumen_soluto, 2), round(volumen_solvente, 2), round(volumen_total, 2)],
        "Masa (kg)": [round(masa_soluto, 2), round(masa_solvente, 2), round(masa_total, 2)]
    })
    st.dataframe(resultados, hide_index=True)

    # Texto de correo
    st.markdown("---")
    st.subheader("📧 Texto del correo sugerido")
    texto_correo = f"""
1. Premisas para la preparación:

a. Densidad del solvente: {densidad_solvente:.1f} kg/m³ (Data JLBT {datetime.today().strftime('%Y-%m-%d')})  
b. Nivel del tanque considerado: {nivel_inicial:.1f} %  
c. Nivel objetivo de aforo: {nivel_final:.1f} %  

2. Preparación de la Solución:

| Componente | Volumen (L) | Masa (kg) |
|------------|-------------|-----------|
| {producto_seleccionado} (soluto) | {volumen_soluto:.2f} | {masa_soluto:.2f} |
| {data["Nombre_solvente"]} | {volumen_solvente:.2f} | {masa_solvente:.2f} |
| Total | {volumen_total:.2f} | {masa_total:.2f} |
"""
    st.code(texto_correo, language="markdown")

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 14px;'>
        📌 Creado por <strong>Denis Sánchez</strong> – Refinería Talara, 2025
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
