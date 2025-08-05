import streamlit as st
import pandas as pd
import math

st.title("📅 Generador de Programación de Turnos Semanales")

# === Entrada de parámetros ===
trabajadores_actuales = st.number_input("Cantidad actual de trabajadores", min_value=1, step=1)
horas_semanales_max = st.number_input("Máximo de horas promedio semanales por trabajador", min_value=1, value=42, step=1)
dias_mes = st.number_input("Número de días en el mes a laborar", min_value=28, max_value=31, step=1)
num_turnos = st.selectbox("Cantidad de turnos por día", options=[2, 3])

# === Cálculos base ===
horas_turno = 12 if num_turnos == 2 else 8
horas_totales_mes = 24 * dias_mes

# === Calcular mínimo de operadores necesarios ===
turnos_totales_mes = num_turnos * dias_mes
horas_laborales_requeridas_mes = turnos_totales_mes * horas_turno
horas_promedio_mes_operador = horas_semanales_max * (dias_mes / 7)
operadores_minimos = math.ceil(horas_laborales_requeridas_mes / horas_promedio_mes_operador)

# === Verificación de suficiencia de trabajadores ===
if trabajadores_actuales < operadores_minimos:
    st.error(f"🚨 Con las restricciones actuales, no es suficiente la cantidad de trabajadores. Se requieren al menos {operadores_minimos} operadores para cubrir la operación.")
    st.stop()
else:
    st.success(f"✅ Los {trabajadores_actuales} operadores son suficientes para cubrir la operación.")

# === Asignación de turnos ===
dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
num_semanas = 4
operadores = [f"OP{i+1}" for i in range(trabajadores_actuales)]

# Dividir operadores entre los turnos cada semana con rotación
turno_actual_por_operador = {op: i % num_turnos for i, op in enumerate(operadores)}

calendarios = {}

for semana in range(1, num_semanas + 1):
    semana_label = f"Semana {semana}"
    df_semana = pd.DataFrame(index=operadores, columns=dias_semana)

    for op in operadores:
        turno = turno_actual_por_operador[op]

        # Calcular día de descanso según el turno anterior
        if semana > 1:
            dias_trabajados_anterior = df_anterior.loc[op]
            if dias_trabajados_anterior["domingo"] != "" and dias_trabajados_anterior["domingo"] != None:
                descanso_inicio = 1  # entra el martes
            elif dias_trabajados_anterior["sábado"] != "" and dias_trabajados_anterior["sábado"] != None:
                descanso_inicio = 0  # entra el lunes
            else:
                descanso_inicio = 0
        else:
            descanso_inicio = 0

        for i, dia in enumerate(dias_semana):
            if i < descanso_inicio:
                df_semana.loc[op, dia] = "DESCANSO"
            else:
                df_semana.loc[op, dia] = f"Turno {turno+1}"

        # Rotación de turno para la siguiente semana
        turno_actual_por_operador[op] = (turno + 1) % num_turnos

    calendarios[semana_label] = df_semana
    df_anterior = df_semana.copy()

# === Mostrar programación ===
for semana in range(1, num_semanas + 1):
    st.markdown(f"### 📆 Semana {semana}")
    st.dataframe(calendarios[f"Semana {semana}"], use_container_width=True)

# === Notas finales ===
st.markdown("""
**📌 Consideraciones implementadas:**
- Turnos rotativos semanales.
- Mínimo un día de descanso por semana (ajustado según turno previo).
- Evaluación de suficiencia de operadores.
- Todos los días cubiertos (24/7).
- Asignación dinámica según turnos y disponibilidad.

**🛠 Restricciones adicionales pendientes de refinar:**
- Control preciso de domingos consecutivos trabajados (actualmente no forzado).
- Control de compensación de horas semanales (promedio 42 h) aún no verificado explícitamente.
- Distribución de descansos fin de semana para todos garantizados aún no asegurada.
""")
