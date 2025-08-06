import streamlit as st
import pandas as pd
import math

st.set_page_config(layout="wide")

# ---
# 1. Data from the provided tables
# ---

current_operators_data = {
    "AYUDANTES": {"FRENTE 1": 6, "FRENTE 3": 6, "FRENTE 4": 6, "PATIO": 0, "Total": 18},
    "ALZADORES": {"FRENTE 1": 6, "FRENTE 3": 0, "FRENTE 4": 0, "PATIO": 0, "Total": 6},
    "TRACTORISTAS": {"FRENTE 1": 9, "FRENTE 3": 15, "FRENTE 4": 18, "PATIO": 3, "Total": 45},
    "SUPERVISORES": {"FRENTE 1": 3, "FRENTE 3": 3, "FRENTE 4": 3, "PATIO": 0, "Total": 9},
    "COSECHADORES": {"FRENTE 1": 0, "FRENTE 3": 7, "FRENTE 4": 10, "PATIO": 0, "Total": 17},
}

required_per_shift_data = {
    "AYUDANTES": {"FRENTE 1": 2, "FRENTE 3": 2, "FRENTE 4": 2, "PATIO": 0},
    "ALZADORES": {"FRENTE 1": 2, "FRENTE 3": 0, "FRENTE 4": 0, "PATIO": 0},
    "TRACTORISTAS": {"FRENTE 1": 3, "FRENTE 3": 5, "FRENTE 4": 6, "PATIO": 3},
    "SUPERVISORES": {"FRENTE 1": 1, "FRENTE 3": 1, "FRENTE 4": 1, "PATIO": 0},
    "COSECHADORES": {"FRENTE 1": 0, "FRENTE 3": 2, "FRENTE 4": 3, "PATIO": 0},
}

# Calculate total required per cargo
total_required_per_cargo = {}
for cargo in required_per_shift_data:
    total_required_per_cargo[cargo] = sum(required_per_shift_data[cargo].values())

# ---
# 2. User Inputs and Configuration
# ---

st.title("👨‍💻 Calculadora de Personal por Cargo y Programador de Turnos")
st.write("Selecciona un cargo y configura los parámetros para el cálculo y la programación.")

st.header("1. Configuración de Turnos y Restricciones")

col1, col2, col3 = st.columns(3)

with col1:
    shift_type = st.selectbox(
        "Tipo de Turnos:",
        ("3 turnos de 8 horas/día", "2 turnos de 12 horas/día", "4 turnos de 6 horas/día")
    )
with col2:
    max_weekly_hours = st.number_input(
        "Máx. de horas promedio a la semana por operador:", min_value=1, value=42, step=1)
with col3:
    selected_cargo = st.selectbox(
        "Selecciona el Cargo a analizar:",
        list(current_operators_data.keys())
    )

if st.button(f"Calcular y Generar Programación para {selected_cargo}"):
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
    
    # --- Step 2: Perform the core calculation based on total hours ---
    required_per_shift = total_required_per_cargo[selected_cargo]
    actual_count = current_operators_data[selected_cargo]["Total"]

    required_weekly_hours_total = required_per_shift * hours_per_shift * 7 # 7 days of coverage
    theoretical_required_operators = required_weekly_hours_total / max_weekly_hours
    total_required = math.ceil(theoretical_required_operators)
    
    # --- Step 3: Display results ---
    st.header("2. Análisis de Requerimiento de Personal")
    st.subheader(f"Análisis para: **{selected_cargo}**")
    
    st.markdown(f"**Cantidad actual de {selected_cargo}:** `{actual_count}`")
    st.markdown(f"**Cantidad de {selected_cargo} requeridos:** `{total_required}`")
    st.markdown(f"**Horas semanales que se deben cubrir (cubriendo 7 días):** `{required_weekly_hours_total:.2f}` horas")

    if actual_count >= total_required:
        st.success(f"✅ ¡La cantidad actual de **{selected_cargo}** es suficiente para cubrir los turnos!")
        deficit = 0
    else:
        st.error(f"❌ La cantidad actual de **{selected_cargo}** es insuficiente para cubrir los turnos.")
        deficit = total_required - actual_count
        st.markdown(f"**Operadores adicionales requeridos:** `{deficit}`")
        
    st.write("---")

    # ---
    # 3. Final Step: Generate Shift Schedule
    # ---
    
    st.header("3. Programación de Turnos (4 Semanas)")
    
    operators_per_shift_group = math.ceil(total_required / num_shifts)
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Generate a schedule for EACH daily shift group
    for shift_index in range(num_shifts):
        
        shift_name = f"Turno {shift_index + 1}"
            
        st.subheader(f"Programación para {shift_name} | Operadores: {operators_per_shift_group}")
        
        schedule_data = {}
        
        for op_index in range(operators_per_shift_group):
            is_additional = op_index >= actual_count / num_shifts
            operator_id = f"OP-{op_index + 1}" if not is_additional else f"OP-AD-{op_index - int(actual_count/num_shifts) + 1}"
            
            operator_schedule = []
            
            # Stagger the start day of each operator's rotation
            stagger_offset = op_index % 7
            
            for week in range(4):
                
                # Determine work days for the week to average 42 hours/week
                if hours_per_shift == 12: # 4 days work / 3 days work pattern
                    days_to_work = 4 if week % 2 == 0 else 3
                else: # Generic pattern for other shifts
                    days_to_work = 5 if week % 2 == 0 else 6
                    
                # Rotate the shift assignment for the week
                assigned_shift = f"Turno {((week + shift_index) % num_shifts) + 1}"

                for day_of_week in range(7):
                    day_in_rotation = (day_of_week + stagger_offset) % 7
                    
                    if day_in_rotation < days_to_work:
                        operator_schedule.append(assigned_shift)
                    else:
                        operator_schedule.append("DESCANSA")
            
            schedule_data[operator_id] = operator_schedule
        
        df = pd.DataFrame(schedule_data, index=[f"Semana {w+1} | {day_names[d]}" for w in range(4) for d in range(7)]).T
        st.dataframe(df)
