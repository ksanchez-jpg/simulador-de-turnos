import streamlit as st
import math

st.set_page_config(layout="wide")

# --- Page Title and Description ---
st.title("👨‍💻 Calculadora de Personal por Cargo")
st.write("Selecciona un cargo para verificar si la cantidad actual de operadores es suficiente para cubrir los turnos.")

# ---
# Data from the provided image
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

st.header("1. Configuración de Turnos")

# Dropdown for shift selection
shift_type = st.selectbox(
    "Tipo de Turnos:",
    ("3 turnos de 8 horas/día", "2 turnos de 12 horas/día", "4 turnos de 6 horas/día")
)

# Define shift hours based on selection
if shift_type == "3 turnos de 8 horas/día":
    hours_per_shift = 8
    num_shifts = 3
elif shift_type == "2 turnos de 12 horas/día":
    hours_per_shift = 12
    num_shifts = 2
else:  # 4 turnos de 6 horas/día
    hours_per_shift = 6
    num_shifts = 4

# Select cargo from the provided list
selected_cargo = st.selectbox(
    "Selecciona el Cargo a analizar:",
    list(cargo_data.keys())
)

# Display current and required per shift for the selected cargo
st.markdown(f"**Cantidad actual de {selected_cargo}:** `{cargo_data[selected_cargo]['actual']}`")
st.markdown(f"**Cantidad requerida por turno de {selected_cargo}:** `{cargo_data[selected_cargo]['requerido_por_turno']}`")

# ---
# 2. Calculation and Results
# ---

st.header("2. Análisis y Resultados")

if st.button(f"Calcular Requerimiento para {selected_cargo}"):
    st.write("---")

    # Get data for the selected cargo
    actual_count = cargo_data[selected_cargo]['actual']
    required_per_shift = cargo_data[selected_cargo]['requerido_por_turno']

    # Total operators needed to cover ALL shifts in a day for this cargo
    total_required_daily = required_per_shift * num_shifts
    
    st.markdown(f"**Total de {selected_cargo} requeridos para un día completo (cubriendo todos los turnos):** `{total_required_daily}`")
    
    # Check if the current number of operators is sufficient
    if actual_count >= total_required_daily:
        st.success(f"✅ ¡La cantidad actual de **{selected_cargo}** es suficiente para cubrir todos los turnos!")
        # Calculate the surplus
        surplus = actual_count - total_required_daily
        st.markdown(f"**Sobran operadores:** `{surplus}`")
    else:
        st.error(f"❌ La cantidad actual de **{selected_cargo}** es insuficiente para cubrir todos los turnos.")
        # Calculate the deficit
        deficit = total_required_daily - actual_count
        st.markdown(f"**Operadores adicionales de {selected_cargo} requeridos:** `{deficit}`")
