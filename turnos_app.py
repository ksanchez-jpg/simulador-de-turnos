import streamlit as st
import pandas as pd
import numpy as np

def run_model():
    st.title("👨‍🔧 Modelo de Planificación de Personal y Turnos")
    st.markdown("---")

    # --- ENTRADAS DEL MODELO ---
    st.header("1. Parámetros del Modelo")

    col1, col2, col3 = st.columns(3)
    with col1:
        cargo_actual = st.text_input("Cargo Actual", "AYUDANTES")
        total_personal_actual = st.number_input("Número total de personal actual", min_value=1, value=178, step=1)
        
    with col2:
        ausentismo_pct = st.number_input("Porcentaje de ausentismo (%)", min_value=0.0, max_value=100.0, value=6.27, step=0.1)
        dias_a_cubrir = st.number_input("Días a cubrir por semana", min_value=1, max_value=7, value=7, step=1)
    
    with col3:
        horas_semanales_promedio = st.number_input("Horas por semana (promedio 3 semanas)", min_value=1, value=42, step=1)
        tipo_turno = st.selectbox("Configuración de turnos por día", ["2 turnos de 12 horas", "3 turnos de 8 horas"])

    st.markdown("---")

    # --- CÁLCULO DE PERSONAL NECESARIO ---
    st.header("2. Cálculo de Personal Requerido")
    
    if tipo_turno == "2 turnos de 12 horas":
        horas_por_dia = 24
        turnos_por_dia = 2
        horas_por_turno = 12
    else: # "3 turnos de 8 horas"
        horas_por_dia = 24
        turnos_por_dia = 3
        horas_por_turno = 8
    
    min_op_por_turno = st.number_input("Cantidad mínima de operadores por turno", min_value=1, value=5, step=1)

    # Calcular las horas requeridas sin ausentismo
    horas_requeridas_por_semana = min_op_por_turno * horas_por_dia * dias_a_cubrir
    
    # Ajustar por ausentismo
    horas_requeridas_con_ausentismo = horas_requeridas_por_semana / (1 - (ausentismo_pct / 100))
    
    # Personal necesario
    personal_necesario = np.ceil(horas_requeridas_con_ausentismo / horas_semanales_promedio).astype(int)

    st.info(f"Para cubrir las necesidades, con un ausentismo del {ausentismo_pct}%, se requieren **{personal_necesario}** operadores para el cargo de **{cargo_actual}**.")

    # Comparación
    if personal_necesario > total_personal_actual:
        st.error(f"⚠️ ¡Atención! El personal actual de {total_personal_actual} es insuficiente. Se necesita contratar o redistribuir **{personal_necesario - total_personal_actual}** personas más.")
    elif personal_necesario < total_personal_actual:
        st.success(f"✅ El personal actual de {total_personal_actual} es suficiente.")
    else:
        st.warning("El personal actual es justo el requerido.")

    st.markdown("---")

    # --- PROGRAMACIÓN DE TURNOS SIMPLIFICADA ---
    st.header("3. Propuesta de Programación de Turnos (Semanal)")

    if personal_necesario > 0:
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        turnos = [f"Turno {i+1} ({horas_por_turno}h)" for i in range(turnos_por_dia)]
        
        # Simulación de equipos para rotación
        equipos = [f"Equipo {i+1}" for i in range(turnos_por_dia + 1)] # Un equipo extra para cubrir descansos

        data_turnos = {
            "Operador": [f"Operador {i+1}" for i in range(personal_necesario)],
            "Equipo": [equipos[i % len(equipos)] for i in range(personal_necesario)]
        }
        df_operadores = pd.DataFrame(data_turnos)

        # Generar un horario de ejemplo para una semana
        horario = pd.DataFrame(index=df_operadores["Operador"], columns=dias_semana)
        
        for idx, row in df_operadores.iterrows():
            equipo = row["Equipo"]
            equipo_idx = int(equipo.split(" ")[1]) - 1

            for i, dia in enumerate(dias_semana):
                turno_asignado = (i + equipo_idx) % (turnos_por_dia + 1)
                
                if turno_asignado < turnos_por_dia:
                    horario.loc[row["Operador"], dia] = turnos[turno_asignado]
                else:
                    horario.loc[row["Operador"], dia] = "DESCANSO"

        st.markdown(f"**Programación de turnos por semana ({tipo_turno}):**")
        st.dataframe(horario.head(20))
        st.markdown("*(Nota: Esta es una programación simplificada para ilustrar la rotación. Un modelo real consideraría las rotaciones mensuales y las horas extra para cumplir el promedio de 42h/semana.)*")
    else:
        st.warning("No se puede generar un horario. Por favor, asegúrate de que se requiere al menos un operador.")

if __name__ == "__main__":
    run_model()
