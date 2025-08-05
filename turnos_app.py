import streamlit as st
import pandas as pd
import math
from datetime import datetime, timedelta

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
    
    # --- Step 3: Perform the core calculation based on total hours ---
    required_per_shift = cargo_data[selected_cargo]['requerido_por_turno']
    required_weekly_hours = required_per_shift * hours_per_shift * num_shifts * days_per_week_to_work
    available_weekly_hours = actual_count * max_weekly_hours
    theoretical_required_operators = required_weekly_hours / max_weekly_hours
    total_required = math.ceil(theoretical_required_operators)
    
    st.subheader(f"Análisis para: **{selected_cargo}**")
    st.markdown(f"**Cantidad actual de {selected_cargo}:** `{actual_count}`")
    st.markdown(f"**Cantidad de {selected_cargo} requeridos:** `{total_required}`")
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
    
    # --- LÓGICA DE PROGRAMACIÓN AJUSTADA ---
    operators_per_shift = math.ceil(total_required / num_shifts)
    
    # Work cycle to average 42 hours/week for 4-week period
    # 12-hour shifts: 4 days (48h) + 3 days (36h) = 84h in 2 weeks -> 42h avg
    # 8-hour shifts: 5 days (40h) + 6 days (48h) + 5 days (40h) + 5 days (40h) -> 168h in 4 weeks -> 42h avg
    
    # The logic below implements a general staggered schedule regardless of shift duration.
    # It ensures a continuous staggered rotation over 4 weeks.
    
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    for shift_index in range(num_shifts):
        st.subheader(f"Programación para Turno {shift_index + 1} ({operators_per_shift} operadores)")
        
        schedule_data = {}
        
        for op_index in range(operators_per_shift):
            operator_id = f"OP-{op_index + 1}"
            
            operator_schedule = []
            
            # This is a key part of the new logic, to create the 4-on/3-on pattern
            # and to stagger the start day of each operator.
            
            start_day_offset = op_index % 7 
            
            for week in range(4):
                is_4_day_week = (week % 2 == 0) # Week 0 and 2 are 4-day weeks, Week 1 and 3 are 3-day weeks
                
                # Check for 12-hour shift type to apply the 4/3 day pattern
                if hours_per_shift == 12:
                    
                    days_to_work_this_week = 4 if is_4_day_week else 3
                    
                    for day_of_week in range(7):
                        day_in_schedule = (day_of_week + start_day_offset) % 7
                        
                        if day_in_schedule < days_to_work_this_week:
                            operator_schedule.append("TRABAJA")
                        else:
                            operator_schedule.append("DESCANSA")
                
                else: # For other shift types, we can use the previous rotation logic
                    total_working_days = math.ceil(max_weekly_hours * 4 / hours_per_shift)
                    cycle_length_days = 28
                    
                    for day_of_week in range(7):
                        day_in_cycle = (day_of_week + week * 7 + op_index) % cycle_length_days
                        
                        if day_in_cycle < total_working_days:
                            operator_schedule.append("TRABAJA")
                        else:
                            operator_schedule.append("DESCANSA")
            
            schedule_data[operator_id] = operator_schedule
        
        df = pd.DataFrame(schedule_data, index=[f"Semana {w+1} | {day_names[d]}" for w in range(4) for d in range(7)]).T
        st.dataframe(df)
