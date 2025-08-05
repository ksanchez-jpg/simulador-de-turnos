# === PROGRAMACIÓN DE TURNOS DETALLADA ===
import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Simulador de Turnos", layout="wide")
st.title("🕒 Programación de Turnos por Semana")

# === Entradas del usuario ===
trabajadores_actuales = st.number_input(
    "Ingrese el número de operadores actuales:",
    min_value=1,
    step=1
)

horas_a_cubrir = st.number_input(
    "¿Cuántas horas deben cubrirse a la semana?",
    min_value=1,
    step=1
)

tipo_turno = st.radio(
    "Seleccione el tipo de turnos:",
    ("2 Turnos de 12h", "3 Turnos de 8h")
)

# Solo se ejecuta si ya se llenaron los campos
if trabajadores_actuales and horas_a_cubrir and tipo_turno:
    st.subheader("📊 Programación Generada Automáticamente")

    # Crear estructura de programación
    num_operadores = trabajadores_actuales
    num_semanas = 4
    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    turnos_diarios = 2 if tipo_turno == "2 Turnos de 12h" else 3

    # Asignar operadores por turno de forma balanceada
    operadores_por_turno = [num_operadores // turnos_diarios] * turnos_diarios
    for i in range(num_operadores % turnos_diarios):
        operadores_por_turno[i] += 1

    # Generar calendarios por semana y turno
    calendarios = {}
    operador_actual = 1
    for semana in range(1, num_semanas + 1):
        for turno in range(1, turnos_diarios + 1):
            n_op = operadores_por_turno[turno - 1]
            df = pd.DataFrame(index=[f"{i+1}" for i in range(n_op)], columns=dias_semana)
            for i in range(n_op):
                for dia in dias_semana:
                    df.loc[f"{i+1}", dia] = operador_actual
                    operador_actual = operador_actual + 1 if operador_actual < num_operadores else 1
            calendarios[f"Semana {semana} - Turno {turno}"] = df

    # Mostrar en orden: primero Semana 1, Turno 1, Turno 2..., luego Semana 2, etc.
    for semana in range(1, num_semanas + 1):
        st.markdown(f"### 📅 Semana {semana}")
        cols = st.columns(turnos_diarios)
        for turno in range(1, turnos_diarios + 1):
            with cols[turno - 1]:
                st.markdown(f"**Turno {turno}**")
                st.dataframe(calendarios[f"Semana {semana} - Turno {turno}"], use_container_width=True)
