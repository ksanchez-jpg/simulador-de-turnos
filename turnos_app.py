import streamlit as st
import math

st.set_page_config(layout="wide")

# --- Page Title and Description ---
st.title("👨‍💻 Planificador de Personal y Turnos")
st.write("Calcula la cantidad de personal requerida para cubrir las horas de operación según el tipo de turno y las horas de trabajo semanales.")

# ---
# User Inputs
# ---

st.header("1. Configuración de Turnos")

# Dropdown for shift selection
shift_type = st.selectbox(
    "Selecciona el tipo de turnos:",
    ("3 turnos de 8 horas/día", "2 turnos de 12 horas/día", "4 turnos de 6 horas/día")
)

# Extract shift duration based on user selection
if shift_type == "3 turnos de 8 horas/día":
    hours_per_shift = 8
elif shift_type == "2 turnos de 12 horas/día":
    hours_per_shift = 12
else: # 4 turnos de 6 horas/día
    hours_per_shift = 6

# Total hours to be covered per day (24 hours)
total_daily_hours = 24

# Number of operators needed to cover one full day of work (24 hours) for one front
min_operators_per_day = math.ceil(total_daily_hours / hours_per_shift)

st.info(f"Para cubrir un día completo con {shift_type}, necesitas al menos **{min_operators_per_day}** operadores por frente por turno.")

# ---
# General Parameters
# ---

st.header("2. Parámetros Generales")

col1, col2, col3 = st.columns(3)

with col1:
    days_per_month = st.number_input("Días del mes a laborar", min_value=1, max_value=31, value=30, step=1)
with col2:
    current_operators = st.number_input("Cantidad actual de operadores", min_value=1, value=65, step=1)
with col3:
    max_weekly_hours = st.number_input("Máximo de horas semanales por operador", min_value=1, value=42, step=1)

# ---
# Calculation and Results
# ---

st.header("3. Análisis de Requerimiento de Personal")

if st.button("Calcular Requerimiento de Personal"):
    st.write("---")

    # --- Calculations ---
    # Total hours to be covered in the month
    required_monthly_hours = total_daily_hours * days_per_month
    
    # Average number of weeks in a month
    weeks_in_month = days_per_month / 7
    
    # Total hours the current staff can cover
    available_monthly_hours = current_operators * max_weekly_hours * weeks_in_month
    
    # --- Results Display ---
    st.subheader("Resultados:")
    
    st.markdown(f"**Horas de operación a cubrir en el mes:** `{required_monthly_hours:.2f}` horas")
    st.markdown(f"**Horas que el personal actual puede cubrir:** `{available_monthly_hours:.2f}` horas")
    
    # Check if current staff is enough
    if available_monthly_hours >= required_monthly_hours:
        st.success("✅ ¡El personal actual es suficiente para cubrir los turnos!")
        # Calculate how many more hours can be covered
        remaining_hours = available_monthly_hours - required_monthly_hours
        extra_personnel_equivalent = remaining_hours / (max_weekly_hours * weeks_in_month)
        st.markdown(f"**Sobran operadores** para cubrir el requerimiento. El excedente es de **`{extra_personnel_equivalent:.2f}`** operadores, aproximadamente.")
    else:
        st.error("❌ El personal actual es insuficiente para cubrir todos los turnos.")
        
        # Calculate the deficit and required additional operators
        hours_deficit = required_monthly_hours - available_monthly_hours
        additional_operators_needed = hours_deficit / (max_weekly_hours * weeks_in_month)
        
        # Display the result
        st.markdown(f"**Horas de déficit:** `{hours_deficit:.2f}` horas")
        st.markdown(f"**Personal adicional requerido:** `{math.ceil(additional_operators_needed)}` operadores")


