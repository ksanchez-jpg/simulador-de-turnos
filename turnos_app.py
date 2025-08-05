# turnos_simulador.py

import streamlit as st
import math
import pandas as pd

st.title("📊 Simulador de Turnos para Tractoristas")
st.markdown("Calculadora de operadores mínimos requeridos sin horas extras")

# === ENTRADAS ===
st.sidebar.header("🔧 Configuración")

# Tipo de turno
tipo_turno = st.sidebar.selectbox("Selecciona tipo de turnos", ["2 Turnos de 12h", "3 Turnos de 8h"])
turnos_por_dia = 2 if tipo_turno == "2 Turnos de 12h" else 3
duracion_turno = 12 if tipo_turno == "2 Turnos de 12h" else 8

# Frentes y requerimientos por turno
st.sidebar.markdown("### Operadores requeridos por frente y turno")
definir_frentes = st.sidebar.checkbox("¿Deseas editar los frentes?", value=False)

if definir_frentes:
    num_frentes = st.sidebar.number_input("Número de frentes", min_value=1, max_value=10, value=4)
    frentes = {}
    for i in range(num_frentes):
        nombre = st.sidebar.text_input(f"Nombre del frente {i+1}", value=f"Frente {i+1}")
        cantidad = st.sidebar.number_input(f"Operadores por turno en {nombre}", min_value=1, value=3)
        frentes[nombre] = cantidad
else:
    frentes = {
        "Frente 1": 3,
        "Frente 3": 5,
        "Frente 4": 6,
        "Patio": 1
    }

# Parámetros generales
dias_mes = st.sidebar.number_input("Días del mes a laborar", min_value=28, max_value=31, value=30)
trabajadores_actuales = st.sidebar.number_input("Cantidad actual de trabajadores", min_value=1, value=45)
horas_max_semanales = st.sidebar.number_input("Máximo de horas promedio semanales por trabajador", min_value=1, value=42)

# === CÁLCULOS ===
# Total de operadores requeridos por día (frentes × turnos)
operadores_por_dia = sum(frentes.values()) * turnos_por_dia

# Total de horas requeridas por mes
total_horas_mes = operadores_por_dia * duracion_turno * dias_mes

# Horas disponibles por trabajador al mes
horas_disponibles_operador = horas_max_semanales * 4

# Cálculo de operadores necesarios
operadores_necesarios = math.ceil(total_horas_mes / horas_disponibles_operador)

# === RESULTADOS ===
st.subheader("📈 Resultados del cálculo")
st.markdown(f"- Total de horas requeridas en el mes: **{total_horas_mes:,} h**")
st.markdown(f"- Horas disponibles por operador al mes: **{horas_disponibles_operador} h**")
st.markdown(f"- Operadores necesarios para cubrir la operación sin horas extras: **{operadores_necesarios}**")
st.markdown(f"- Diferencia con los operadores actuales ({trabajadores_actuales}): **{operadores_necesarios - trabajadores_actuales:+} operadores**")

if trabajadores_actuales < operadores_necesarios:
    st.error("🚨 No cuentas con suficiente personal para cubrir los turnos sin hacer horas extras ni dejar vacíos.")
else:
    st.success("✅ El personal actual es suficiente para cubrir la operación cumpliendo las restricciones.")

# === Tabla resumen por frente ===
df_frentes = pd.DataFrame({
    "Frente": list(frentes.keys()),
    "Operadores por turno": list(frentes.values()),
    "Turnos por día": [turnos_por_dia] * len(frentes),
    "Total operadores por día": [v * turnos_por_dia for v in frentes.values()],
})
st.markdown("### 📋 Resumen de frentes")
st.dataframe(df_frentes, use_container_width=True)

import pandas as pd

# === PARÁMETROS ===
turnos = ["T1", "T2", "T3"]  # Cambiar a 2 turnos si es de 12h
num_turnos = len(turnos)
dias_mes = 30
semanas = 4
operadores_necesarios = 48  # Valor desde cálculo previo

# === GENERAR OPERADORES ===
operadores = [f"OP{str(i+1).zfill(2)}" for i in range(operadores_necesarios)]

# === DIVIDIR OPERADORES EN GRUPOS PARA TURNOS ===
grupo_por_turno = operadores_necesarios // num_turnos
grupos = [operadores[i * grupo_por_turno:(i + 1) * grupo_por_turno] for i in range(num_turnos)]

# === GENERAR PROGRAMACIÓN CON ROTACIÓN Y DESCANSO ===
programacion = []

for semana in range(semanas):
    for turno_idx, grupo in enumerate(grupos):
        turno_actual = turnos[(turno_idx + semana) % num_turnos]
        for op in grupo:
            descanso = (hash(op) + semana) % 7  # Día de descanso rotativo
            for dia in range(7):
                dia_mes = semana * 7 + dia
                if dia_mes >= dias_mes:
                    break
                turno = "D" if dia == descanso else turno_actual
                programacion.append({
                    "Semana": semana + 1,
                    "Día del mes": dia_mes + 1,
                    "Operador": op,
                    "Turno asignado": turno
                })

# === CREAR DATAFRAME ===
df_programacion = pd.DataFrame(programacion)

# === MOSTRAR EN STREAMLIT ===
import streamlit as st

st.subheader("📅 Programación mensual de turnos por operador")
st.dataframe(df_programacion, use_container_width=True)


