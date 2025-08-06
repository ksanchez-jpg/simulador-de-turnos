import streamlit as st
import pandas as pd
import math
from datetime import datetime, timedelta

# ---
# 1. User Inputs and Configuration
# ---

st.title("👨‍💻 Calculadora de Personal y Programador de Turnos")
st.write("Ingresa los parámetros de tu operación para calcular el personal requerido y generar los turnos.")

st.header("1. Configuración de Turnos y Personal")

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
    required_per_shift = st.number_input(
        "Operadores requeridos por turno (por día):", min_value=1, value=15, step=1)
    
st.write("---")
st.subheader("Personal actual")

col4, col5 = st.columns(2)
with col4:
    actual_count = st.number_input(
        "Cantidad total de personal actual:", min_value=0, value=45, step=1)
with col5:
    coverage_days_per_week = st.number_input(
        "Días a laborar por semana para cobertura:", min_value=1, max_value=7, value=7, step=1)

# ---
# 2. Calculation and Results
# ---

st.header("2. Análisis de Requerimiento de Personal")

if st.button(f"Calcular y Generar Programación"):
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
    required_weekly_hours_total = required_per_shift * hours_per_shift * num_shifts * coverage_days_per_week
    theoretical_required_operators = required_weekly_hours_total / max_weekly_hours
    total_required = math.ceil(theoretical_required_operators)
    
    available_weekly_hours = actual_count * max_weekly_hours

    # --- Step 3: Display results ---
    st.subheader(f"Resultados del Cálculo:")
    
    st.markdown(f"**Personal requerido por turno (ingresado):** `{required_per_shift}`")
    st.markdown(f"**Cantidad de operadores requeridos (teórico):** `{total_required}`")
    st.markdown(f"**Cantidad de personal actual:** `{actual_count}`")
    st.markdown(f"**Horas semanales que se deben cubrir:** `{required_weekly_hours_total:.2f}` horas")

    if actual_count >= total_required:
        st.success(f"✅ ¡El personal actual es suficiente!")
        deficit = 0
    else:
        st.error(f"❌ El personal actual es insuficiente.")
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
            # Differentiate between current and additional staff
            is_additional = (op_index + 1) > math.ceil(actual_count / num_shifts)
            
            operator_id = f"OP-{op_index + 1}" if not is_additional else f"OP-AD-{op_index - math.ceil(actual_count / num_shifts) + 1}"
            
            operator_schedule = []
            
            stagger_offset = op_index % 7
            
            for week in range(4):
                if hours_per_shift == 12: 
                    days_to_work = 4 if week % 2 == 0 else 3
                else: 
                    # Default balanced pattern for other shifts to meet 42h average
                    if max_weekly_hours == 42:
                        days_to_work_for_cycle = math.ceil(max_weekly_hours * 4 / hours_per_shift)
                        days_to_work = days_to_work_for_cycle // 4
                    else:
                        days_to_work = math.ceil(max_weekly_hours / hours_per_shift)
                
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
