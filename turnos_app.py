# turnos_app.py

import streamlit as st
import math
import pandas as pd

st.title("📊 Simulador de Turnos para Tractoristas")
st.markdown("Prototipo de asignación de turnos con jornada de 42h semanales (Colombia 2026)")

# === ENTRADAS ===
st.sidebar.header("🔧 Configuración")

# Tipo de turno
tipo_turno = st.sidebar.selectbox("Selecciona tipo de turnos", ["2 Turnos de 12h", "3 Turnos de 8h"])

# Frentes y requerimientos por turno
frentes = {
    "Frente 1": 3,
    "Frente 3": 5,
    "Frente 4": 6,
    "Patio": 1
}

# Cálculo de requerimientos diarios
turnos_por_dia = 2 if tipo_turno == "2 Turnos de 12h" else 3
duracion_turno = 12 if tipo_turno == "2 Turnos de 12h" else 8

dias_mes = st.sidebar.number_input("Días del mes", min_value=28, max_value=31, value=30)
trabajadores_actuales = st.sidebar.number_input("Cantidad de trabajadores actuales", min_value=1, value=45)
horas_max_semanales = st.sidebar.number_input("Máximo de horas semanales por trabajador", min_value=1, value=42)

# === CÁLCULOS ===
# Total de horas requeridas por mes
operadores_por_dia = sum(v for v in frentes.values()) * turnos_por_dia
horas_totales_mes = operadores_por_dia * duracion_turno * dias_mes

# Horas disponibles por operador al mes
horas_disponibles_operador = horas_max_semanales * 4
operadores_necesarios = math.ceil(horas_totales_mes / horas_disponibles_operador)

# === RESULTADOS ===
st.subheader("📈 Resultados")
st.markdown(f"- Total de horas requeridas en el mes: **{horas_totales_mes:,} h**")
st.markdown(f"- Horas disponibles por operador al mes: **{horas_disponibles_operador} h**")
st.markdown(f"- Operadores necesarios para cubrir la operación: **{operadores_necesarios}**")
st.markdown(f"- Diferencia con los actuales ({trabajadores_actuales}): **{operadores_necesarios - trabajadores_actuales:+} operadores**")

if trabajadores_actuales < operadores_necesarios:
    st.warning("⚠️ No cuentas con suficiente personal para cubrir los turnos sin hacer horas extras.")
else:
    st.success("✅ El personal actual es suficiente para cubrir los turnos según las restricciones.")

# === Tabla resumen (opcional) ===
df_frentes = pd.DataFrame({
    "Frente": list(frentes.keys()),
    "Operadores por turno": list(frentes.values()),
    "Turnos diarios": [turnos_por_dia] * len(frentes),
    "Total operadores/día": [v * turnos_por_dia for v in frentes.values()],
})
st.dataframe(df_frentes, use_container_width=True)

