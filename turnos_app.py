import streamlit as st
import pandas as pd
import math

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

st.title("👨‍💻 Calculadora de Personal por Cargo y Programador de Turnos")
st.write("Selecciona un cargo y configura las horas para verificar si el personal actual es suficiente.")

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
    required_weekly_hours = required_per_shift * hours_per_shift * num_shifts * days_per_week_to_work
    available_weekly_hours = actual_count * max_weekly_hours
    theoretical_required_operators = required_weekly_hours / max_weekly_hours
    
    st.subheader(f"Análisis para: **{selected_cargo}**")
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
        
    # ---
    # 3. Final Step: Generate Shift Schedule
    # ---
    
    st.header("3. Programación de Turnos (4 Semanas)")
    
    # --- NUEVA LÓGICA DE CÁLCULO ---
    # La cantidad de operadores por turno es el requerimiento por turno de la tabla
    # del usuario.
    operators_per_shift = required_per_shift

    # Define the working cycle (e.g., 21 working days over 4 weeks for 42 hours/week)
    total_working_days = math.ceil(max_weekly_hours * 4 / hours_per_shift)
    cycle_length_days = 28 # Total days in 4 weeks
    
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Generate a schedule for EACH daily shift group
    for shift_index in range(num_shifts):
        st.subheader(f"Programación para Turno {shift_index + 1} ({operators_per_shift} operadores)")
        
        schedule_data = {}
        
        # This part ensures that operators are correctly divided
        for op_index in range(operators_per_shift):
            operator_id = f"OP-{op_index + 1}"
            
            operator_schedule = []
            
            # Use a staggered start day for each operator within the group
            start_day_offset = (op_index) % cycle_length_days
            
            for week in range(4):
                for day_of_week in range(7):
                    day_in_cycle = (day_of_week + week * 7 + start_day_offset) % cycle_length_days
                    
                    # Apply the working day logic
                    if day_in_cycle < total_working_days:
                        operator_schedule.append("TRABAJA")
                    else:
                        operator_schedule.append("DESCANSA")
            
            schedule_data[operator_id] = operator_schedule
        
        # Create a DataFrame for a better visualization
        df = pd.DataFrame(schedule_data, index=[f"Semana {w+1} | {day_names[d]}" for w in range(4) for d in range(7)]).T
        st.dataframe(df)
