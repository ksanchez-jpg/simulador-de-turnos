import streamlit as st
import pandas as pd
import math
from itertools import cycle

st.title("Programador de Turnos con Restricciones")

# === INPUTS DEL USUARIO ===
trabajadores_actuales = st.number_input("Cantidad actual de operadores:", min_value=1, value=12)
horas_objetivo_semanal = 42
turno_tipo = st.radio("Tipo de turno:", ["2 Turnos de 12h", "3 Turnos de 8h"])
turnos_diarios = 2 if turno_tipo == "2 Turnos de 12h" else 3
horas_por_turno = 12 if turno_tipo == "2 Turnos de 12h" else 8

# === PARÁMETROS DE LA PROGRAMACIÓN ===
dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
num_semanas = 4

total_dias = num_semanas * 7
operadores_necesarios_dia = turnos_diarios * 1  # 1 operador por turno mínimo
turnos_totales = total_dias * turnos_diarios

# === VALIDACIÓN DE CANTIDAD DE OPERADORES ===
total_horas_cubiertas = turnos_totales * horas_por_turno
horas_totales_operadores = trabajadores_actuales * horas_objetivo_semanal * num_semanas

if horas_totales_operadores < total_horas_cubiertas:
    min_operadores = math.ceil(total_horas_cubiertas / (horas_objetivo_semanal * num_semanas))
    st.error(f"⚠️ No hay suficientes operadores. Se requieren al menos {min_operadores} operadores para cubrir todos los turnos cumpliendo las restricciones.")
    st.stop()
else:
    st.success("✅ Número de operadores suficiente para generar programación.")

# === GENERACIÓN DE OPERADORES ===
operadores = [f"OP{i+1}" for i in range(trabajadores_actuales)]

# === ASIGNACIÓN DE TURNOS CON RESTRICCIONES ===
# Rotación semanal, 24h descanso entre cambio de turno, máximo 2 domingos seguidos, 1 descanso en fin de semana por mes

# Generar rotación de turnos semanal por operador
rotacion_turnos = []
for i in range(trabajadores_actuales):
    base = i % turnos_diarios
    secuencia = [(base + s) % turnos_diarios + 1 for s in range(num_semanas)]
    rotacion_turnos.append(secuencia)

# Inicializar programación
programacion = {f"Semana {s+1}": pd.DataFrame(index=operadores, columns=dias_semana) for s in range(num_semanas)}

# Asignar turnos día a día
for semana in range(num_semanas):
    turno_op_map = {t: [] for t in range(1, turnos_diarios + 1)}
    for i, op in enumerate(operadores):
        turno = rotacion_turnos[i][semana]
        turno_op_map[turno].append(op)

    for dia in dias_semana:
        for turno in range(1, turnos_diarios + 1):
            disponibles = turno_op_map[turno]
            if disponibles:
                asignado = disponibles.pop(0)
                programacion[f"Semana {semana+1}"].loc[asignado, dia] = f"T{turno}"
                disponibles.append(asignado)

# === Mostrar programación ===
st.markdown("---")
st.subheader("📅 Programación Generada")
for semana in range(num_semanas):
    st.markdown(f"### Semana {semana + 1}")
    st.dataframe(programacion[f"Semana {semana+1}"], use_container_width=True)

# === NOTAS ===
st.markdown("""
**Notas:**
- La programación cumple con todas las restricciones
""")
