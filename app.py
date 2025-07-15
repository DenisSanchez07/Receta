import streamlit as st
import pandas as pd
import math

# Título de la app
st.title("Preparación de Soluciones Químicas")

# Cargar la plantilla Excel
@st.cache_data
def cargar_datos():
    return pd.read_excel("plantilla_recetas_productos.xlsx")

df = cargar_datos()

# Seleccionar unidad
unidad = st.selectbox("Selecciona la unidad:", df["Unidad"].unique())

# Filtrar productos por unidad
productos_unidad = df[df["Unidad"] == unidad]
producto = st.selectbox("Selecciona el producto químico:", productos_unidad["Nombre_comercial"].unique())

# Obtener los datos del producto seleccionado
data = productos_unidad[productos_unidad["Nombre_comercial"] == producto].iloc[0]

tipo_producto = data["Tipo_Producto"]
densidad_soluto = data["Densidad_Soluto"]
densidad_solvente_ref = data["Densidad_Solvente_Referencia"]
concentracion = data["Concentracion_Porcentual"] / 100
formula_volumen = data["Ecuacion_Volumen"]
codigo = data["Codigo"]
proveedor = data["Proveedor"]
presentacion = data["Presentacion"]

st.markdown(f"**Tipo de producto:** {tipo_producto}")

# Ingresar niveles
nivel_inicial = st.number_input("Nivel inicial (%):", min_value=0.0, max_value=100.0, value=15.0)
nivel_final = st.number_input("Nivel final (%):", min_value=0.0, max_value=100.0, value=88.0)

# Calcular volumen
try:
    x = nivel_final
    V_final = eval(formula_volumen)
    x = nivel_inicial
    V_inicial = eval(formula_volumen)
    volumen_solucion = round(V_final - V_inicial, 4)
except:
    st.error("Error al evaluar la fórmula del volumen. Verifica el formato.")
    volumen_solucion = 0

# Calcular masas
masa_total = round(volumen_solucion * densidad_solvente_ref, 2)
masa_soluto = round(masa_total * concentracion, 2)
masa_solvente = round(masa_total - masa_soluto, 2)

densidad_real = round((masa_soluto + masa_solvente) / volumen_solucion, 3)

# Mostrar tabla
st.subheader("Resultados de la preparación")
resultados = pd.DataFrame({
    "Componente": ["Soluto", "Solvente", "Solución Total"],
    "Volumen [L]": [round(masa_soluto / densidad_soluto * 1000, 2), round(masa_solvente / densidad_solvente_ref * 1000, 2), round(volumen_solucion * 1000, 2)],
    "Masa [kg]": [masa_soluto, masa_solvente, masa_soluto + masa_solvente]
})
st.dataframe(resultados)

# Mostrar correo técnico
date_str = pd.Timestamp.today().strftime("%Y-%m-%d")
correo = f"""
1.         Premisas para la preparación:
 
a. Densidad de la nafta pesada hidrotratada: {densidad_solvente_ref} kg/m3 (Data JLBT {date_str}).
b. Nivel del drum {unidad} a considerar {nivel_inicial:.1f} %.
c. Objetivo para aforar es hasta el {nivel_final:.1f}% del nivel, para utilizar la máxima cantidad del PQ una vez abierto el cilindro, que sea fácil de contabilizar en campo y estar por debajo de la alarma de alta (90%).
 
2.         Preparación de la Solución:
 
a. Volumen para usar de {producto}:
{round(masa_soluto / densidad_soluto * 1000)} L ({masa_soluto} kg).        
b. Volumen para usar de nafta pesada hidrotratada:
{round(masa_solvente / densidad_solvente_ref * 1000)} L ({masa_solvente} kg).
c. Volumen total de solución:
{round(volumen_solucion * 1000)} L ({round(masa_soluto + masa_solvente, 2)} kg).                            
 
3.         Información para retirar producto de almacén (JIYA):
 
a. Código Material: {codigo}.
b. Proveedor: {proveedor}.
c. Nombre comercial: {producto}.
d. Presentación: {presentacion}.
"""

st.subheader("Texto generado para correo técnico")
st.text_area("Correo:", correo, height=400)

# Firma final
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 14px;">
        📌 Creado por <strong>Denis Sánchez</strong> – Refinería Talara, 2025
    </div>
    """,
    unsafe_allow_html=True
)
