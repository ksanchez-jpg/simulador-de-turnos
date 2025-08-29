import streamlit as st
import math
import pandas as pd
import random

# Título de la aplicación
st.title("Calculadora de Personal y Programación de Turnos")
st.write("Ingrese los parámetros a continuación para calcular el personal necesario y generar la programación de turnos.")

# --- Sección de Parámetros de Entrada ---
st.header("Parámetros de la Programación")

# Campos de entrada de texto para el cargo
cargo = st.text_input("Cargo del personal (ej: Operador de Máquina)", "Operador")

# Campos de entrada numéricos con valores mínimos y máximos
personal_actual = st.number_input("Cantidad de personal actual en el cargo", min_value=0, value=1)
ausentismo_porcentaje = st.number_input("Porcentaje de ausentismo (%)", min_value=0.0, max_value=100.0, value=5.0)
dias_a_cubrir = st.number_input("Días a cubrir por semana", min_value=1, max_value=7, value=7)
horas_promedio_semanal = st.number_input("Horas promedio semanales por operador (últimas 3 semanas)", min_value=1, value=42)
personal_vacaciones = st.number_input("Personal de vacaciones en el período de programación", min_value=0, value=0)
operadores_por_turno = st.number_input("Cantidad de operadores requeridos por turno", min_value=1, value=1)

# Selección de turnos y validación de horas por turno
st.subheader("Configuración de Turnos")
cantidad_turnos = st.selectbox("Cantidad de turnos", [2, 3, "Mix"], index=1)
if cantidad_turnos == 3:
    horas_por_turno = 8
    st.write("Horas por turno (automático): 8 horas (para 3 turnos)")
elif cantidad_turnos == 2:
    horas_por_turno = 12
    st.write("Horas por turno (automático): 12 horas (para 2 turnos)")
else:
    # Lógica para turnos mixtos de 8 y 12 horas
    horas_por_turno = 12
    st.write("Horas por turno (automático): Combinación de 8 y 12 horas para un promedio balanceado.")

# --- Lógica de Cálculo y Programación ---
def run_calculation(use_actual_personnel):
    # Initialize the dictionary to store dataframes
    all_turnos_dfs = {}
    try:
        # Validación de valores para evitar errores de cálculo
        if personal_actual <= 0 or dias_a_cubrir <= 0 or horas_promedio_semanal <= 0 or operadores_por_turno <= 0:
            st.error("Por favor, ingrese valores válidos mayores a cero.")
            return

        # --- Lógica de Cálculo ---
        horas_operacion_diarias = cantidad_turnos * horas_por_turno if cantidad_turnos != "Mix" else 24
        horas_trabajo_totales_semanales = dias_a_cubrir * horas_operacion_diarias * operadores_por_turno
        personal_teorico = horas_trabajo_totales_semanales / horas_promedio_semanal
        
        factor_ausentismo = 1 - (ausentismo_porcentaje / 100)
        if factor_ausentismo <= 0:
             st.error("El porcentaje de ausentismo no puede ser 100% o más. Por favor, ajuste el valor.")
             return
        
        personal_ajustado_ausentismo = personal_teorico / factor_ausentismo
        personal_final_necesario = round(personal_ajustado_ausentismo + personal_vacaciones)

        personal_a_usar = personal_actual if use_actual_personnel else personal_final_necesario
        
        # Validar que el personal necesario sea suficiente para cubrir los turnos
        if personal_a_usar < operadores_por_turno * (3 if cantidad_turnos != "Mix" else 2):
            st.error(f"Error: El personal requerido ({personal_a_usar}) no es suficiente para cubrir los {operadores_por_turno} operadores por turno en {cantidad_turnos} turnos.")
            return
        
        # --- Sección de Resultados ---
        st.header("Resultados del Cálculo")
        if not use_actual_personnel:
            st.metric(label="Personal Requerido para no generar horas extras", value=f"{personal_a_usar} persona(s)")
        else:
             st.metric(label="Personal Usado para la Programación", value=f"{personal_a_usar} persona(s)")
        
        st.metric(label=f"Horas de trabajo totales requeridas a la semana para {cargo}", value=f"{horas_trabajo_totales_semanales} horas")
        
        if not use_actual_personnel:
            diferencia_personal = personal_a_usar - personal_actual
            if diferencia_personal > 0:
                st.warning(f"Se necesitan **{diferencia_personal}** personas adicionales para cubrir la operación.")
            elif diferencia_personal < 0:
                st.info(f"Tienes **{abs(diferencia_personal)}** personas de más, lo que podría reducir costos o permitir más personal de reserva.")
            else:
                st.success("¡El personal actual es el ideal para esta operación!")
        
        # --- Programación de Turnos Sugerida con Descanso Rotativo y Balance de Horas ---
        st.header("Programación de Turnos Sugerida (basada en el personal requerido)")
        
        turnos_horarios = []
        if cantidad_turnos == 3:
            turnos_horarios = ["06:00 - 14:00",]()_
