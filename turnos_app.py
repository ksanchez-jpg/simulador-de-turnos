import streamlit as st
import math

st.set_page_config(layout="wide")

# --- Page Title and Description ---
st.title("👨‍💻 Calculadora de Personal por Cargo")
st.write("Selecciona un cargo y configura las horas para verificar si el personal actual es suficiente.")

# ---
# Data from the provided image (fixed data for demonstration)
# ---
cargo_data = {
    "COSECHADORES": {"actual": 17, "requerido_por_turno": 5},
    "TRACTORISTAS": {"actual": 45, "requerido_por_turno": 15},
    "ALZADORES": {"actual": 6, "requerido_por_turno": 2},
    "SUPERVISORES": {"actual": 9, "requerido_por_turno": 3},
    "AYUDANTES": {"actual": 18, "requerido_por_turno": 6}
}

# ---
# 1. User Inputs
# ---

st.header("1. Configuración de Turnos y Restricciones")

col1, col2, col3, col4 = st.columns(4)

with col1:
    shift_type = st.selectbox(
        "Tipo de Turnos:",
        ("3 turnos de 8 horas/día", "2 turnos de 12 horas/día", "4 turnos de 6 horas/día")
    )
with col2:
    days_per_week_to_work = st.number_input(
        "Días a laborar por semana:", min_value=1, max_value=7, value=6, step=1)
with col3:
    max_weekly_hours = st.number_input(
        "Máx. de horas promedio a la semana por operador:", min_value=1, value=42, step=1)
with col4:
    selected_cargo = st.selectbox(
        "Selecciona el Cargo a analizar:",
        list(cargo_data.keys())
    )

# ---
# 2. Calculation and Results
# ---

st.header("2. Análisis de Requerimiento de Personal")

if st.button(f"Calcular Requerimiento para {selected_cargo}"):
    st.write("---")

    # --- Step 1: Define shift hours and number of shifts ---
    if shift_type == "3 turnos de 8 horas/día":
        hours_per_shift = 8
        num_shifts = 3
    elif shift_type == "2 turnos de 12 horas/día":
        hours_per_shift = 12
        num_shifts = 2
    else:  # 4 turnos de 6 horas/día
        hours_per_shift = 6
        num_shifts = 4
    
    # --- Step 2: Extract data for the selected cargo ---
    actual_count = cargo_data[selected_cargo]['actual']
    required_per_shift = cargo_data[selected_cargo]['requerido_por_turno']

    # --- Step 3: Perform the core calculation based on total hours ---
    
    # Total hours to be covered per week for this specific cargo
    required_weekly_hours = required_per_shift * hours_per_shift * num_shifts * days_per_week_to_work

    # Total hours the current staff can cover per week
    available_weekly_hours = actual_count * max_weekly_hours

    # Theoretical number of operators required to cover the required weekly hours
    theoretical_required_operators = required_weekly_hours / max_weekly_hours
    
    # --- Step 4: Display results and conclusion ---
    st.subheader(f"Análisis para: **{selected_cargo}**")
    
    # Displaying actual vs. required operators for clarity
    st.markdown(f"**Cantidad actual de {selected_cargo}:** `{actual_count}`")
    st.markdown(f"**Cantidad de {selected_cargo} requeridos:** `{math.ceil(theoretical_required_operators)}`")

    st.markdown(f"**Horas semanales que se deben cubrir:** `{required_weekly_hours:.2f}` horas")
    st.markdown(f"**Horas semanales que el personal actual puede cubrir:** `{available_weekly_hours:.2f}` horas")
    

    if available_weekly_hours >= required_weekly_hours:
        st.success(f"✅ ¡La cantidad actual de **{selected_cargo}** es suficiente para cubrir los turnos!")
        surplus = actual_count - theoretical_required_operators
        st.markdown(f"**Sobran operadores:** `{surplus:.2f}` operadores.")
    else:
        st.error(f"❌ La cantidad actual de **{selected_cargo}** es insuficiente para cubrir los turnos.")
        deficit = theoretical_required_operators - actual_count
        st.markdown(f"**Operadores adicionales requeridos:** `{math.ceil(deficit)}`")
