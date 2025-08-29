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

# --- Utilidad: horas del turno según configuración/semana ---
def horas_turno_actual(cfg, turno_idx, semana_idx, horas_base):
    """
    cfg: 2, 3 o 'Mix'
    turno_idx: 0,1,2
    semana_idx: 0,1,2
    horas_base: 8 u 12 (según cfg 2/3)
    """
    if cfg == "Mix":
        # Semana 1: 2 turnos de 12h (turno 0 y 1), turno 2 descansa.
        # Semanas 2 y 3: 3 turnos de 8h.
        if semana_idx == 0:
            return 12 if turno_idx in (0, 1) else 0
        else:
            return 8
    else:
        # En 2 turnos siempre 12h; en 3 turnos siempre 8h
        return horas_base

# --- Lógica de Cálculo y Programación ---
def run_calculation(use_actual_personnel):
    all_turnos_dfs = {}
    try:
        # Validación de valores para evitar errores de cálculo
        if personal_actual <= 0 or dias_a_cubrir <= 0 or horas_promedio_semanal <= 0 or operadores_por_turno <= 0:
            st.error("Por favor, ingrese valores válidos mayores a cero.")
            return

        # --- Cálculo de personal requerido (con parámetros ingresados) ---
        horas_operacion_diarias = (cantidad_turnos * horas_por_turno) if cantidad_turnos != "Mix" else 24
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
        min_turnos = (cantidad_turnos if cantidad_turnos != "Mix" else 2)  # en semana 1 de Mix hay 2 turnos
        if personal_a_usar < operadores_por_turno * min_turnos:
            st.error(
                f"Error: El personal usado ({personal_a_usar}) no es suficiente para cubrir "
                f"{operadores_por_turno} operadores por turno en {cantidad_turnos} turnos."
            )
            return

        # --- Resultados del cálculo ---
        st.header("Resultados del Cálculo")
        if not use_actual_personnel:
            st.metric(label="Personal Requerido para no generar horas extras", value=f"{personal_a_usar} persona(s)")
        else:
            st.metric(label="Personal Usado para la Programación", value=f"{personal_a_usar} persona(s)")

        st.metric(
            label=f"Horas de trabajo totales requeridas a la semana para {cargo}",
            value=f"{horas_trabajo_totales_semanales} horas"
        )

        if not use_actual_personnel:
            diferencia_personal = personal_a_usar - personal_actual
            if diferencia_personal > 0:
                st.warning(f"Se necesitan **{diferencia_personal}** personas adicionales para cubrir la operación.")
            elif diferencia_personal < 0:
                st.info(f"Tienes **{abs(diferencia_personal)}** personas de más, lo que podría reducir costos o permitir más personal de reserva.")
            else:
                st.success("¡El personal actual es el ideal para esta operación!")

        # --- Programación de Turnos Sugerida equilibrando horas ---
        st.header("Programación de Turnos Sugerida (balanceada)")

        if cantidad_turnos == 3:
            turnos_horarios = ["06:00 - 14:00", "14:00 - 22:00", "22:00 - 06:00"]
        elif cantidad_turnos == 2:
            turnos_horarios = ["06:00 - 18:00", "18:00 - 06:00"]
        else:
            turnos_horarios = ["06:00 - 14:00 (8h/sem 2-3)", "14:00 - 22:00 (8h/sem 2-3)", "22:00 - 06:00 (8h/sem 2-3)"]

        dias_a_programar = dias_a_cubrir * 3
        dias_semana_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        columnas_dias = [f"{dias_semana_nombres[d % 7]} Sem{d // 7 + 1}" for d in range(dias_a_programar)]

        # --- Meta de horas por operador: 128h en 3 semanas ---
        horas_totales_por_operador = 128
        st.info(
            f"Cada operador trabajará objetivo **{horas_totales_por_operador}h** en 3 semanas "
            f"(≈{horas_totales_por_operador/3:.2f} h/promedio semanal). "
            "La asignación diaria prioriza a quienes tienen menos horas acumuladas."
        )

        horas_trabajadas_por_operador = {op_idx: 0 for op_idx in range(personal_a_usar)}

        # Reparto de personal por turno (grupos de operadores)
        total_turnos_config = (cantidad_turnos if cantidad_turnos != "Mix" else 3)
        base_empleados_por_turno = personal_a_usar // total_turnos_config
        resto_empleados = personal_a_usar % total_turnos_config

        start_index_global = 0
        for i in range(total_turnos_config):
            num_empleados_este_turno = base_empleados_por_turno + (1 if i < resto_empleados else 0)
            end_index_global = start_index_global + num_empleados_este_turno

            st.subheader(f"Tabla Turno {i + 1}: {turnos_horarios[i]}")
            data = {'Operador': [f"{cargo} {op_idx + 1}" for op_idx in range(start_index_global, end_index_global)]}
            df_turno = pd.DataFrame(data)

            for dia in range(dias_a_programar):
                columna = columnas_dias[dia]
                semana = dia // dias_a_cubrir

                # Horas del turno según config y semana
                h_shift = horas_turno_actual(cantidad_turnos, i, semana, horas_por_turno)

                # Si este turno no opera (ej. turno 3 en semana 1 de Mix), todos descansan
                if h_shift == 0 or num_empleados_este_turno == 0:
                    df_turno[columna] = ["Descanso"] * num_empleados_este_turno
                    continue

                # Cantidad a trabajar hoy en este turno (no puede exceder el personal de ese turno)
                num_trabajando = min(operadores_por_turno, num_empleados_este_turno)

                # Índices globales de los operadores del turno
                op_indices = list(range(start_index_global, end_index_global))

                # Ordenar priorizando a quienes tienen menos horas; desempate rotando por día
                # Primero los que están por debajo de la meta, luego (si se requiere) los que ya alcanzaron meta
                below_target = [op for op in op_indices if horas_trabajadas_por_operador[op] < horas_totales_por_operador]
                at_or_above = [op for op in op_indices if horas_trabajadas_por_operador[op] >= horas_totales_por_operador]

                below_target_sorted = sorted(
                    below_target,
                    key=lambda op: (horas_trabajadas_por_operador[op], (op + dia) % 100000)
                )
                at_or_above_sorted = sorted(
                    at_or_above,
                    key=lambda op: (horas_trabajadas_por_operador[op], (op + dia) % 100000)
                )

                orden_prioridad = below_target_sorted + at_or_above_sorted
                trabajando_hoy = set(orden_prioridad[:num_trabajando])

                dia_programacion = []
                for j in range(num_empleados_este_turno):
                    global_op_idx = start_index_global + j
                    if global_op_idx in trabajando_hoy:
                        dia_programacion.append(f"Turno {i + 1}")
                        horas_trabajadas_por_operador[global_op_idx] += h_shift
                    else:
                        dia_programacion.append("Descanso")

                df_turno[columna] = dia_programacion

            # Totales por operador (para este grupo/turno)
            total_horas = [horas_trabajadas_por_operador[op_idx] for op_idx in range(start_index_global, end_index_global)]
            promedio_semanal = [h / 3 for h in total_horas]

            df_turno['Total Horas'] = total_horas
            df_turno['Promedio Semanal'] = [f"{ps:.2f}" for ps in promedio_semanal]

            st.dataframe(df_turno, hide_index=True, use_container_width=True)

            all_turnos_dfs[f"Turno {i + 1}"] = df_turno
            start_index_global = end_index_global

        # Resumen global (verifica la igualdad final)
        resumen = pd.DataFrame({
            "Operador": [f"{cargo} {i+1}" for i in range(personal_a_usar)],
            "Horas Totales (3 semanas)": [horas_trabajadas_por_operador[i] for i in range(personal_a_usar)],
            "Promedio Semanal": [round(horas_trabajadas_por_operador[i] / 3, 2) for i in range(personal_a_usar)]
        }).sort_values(["Horas Totales (3 semanas)", "Operador"]).reset_index(drop=True)

        st.subheader("Resumen Global de Horas por Operador")
        st.dataframe(resumen, hide_index=True, use_container_width=True)

        min_h = resumen["Horas Totales (3 semanas)"].min()
        max_h = resumen["Horas Totales (3 semanas)"].max()
        st.caption(f"Balance final: mínimo {min_h}h, máximo {max_h}h en 3 semanas (diferencia {max_h - min_h}h).")

    except Exception as e:
        st.error(f"Ha ocurrido un error en el cálculo. Por favor, revise los valores ingresados. Error: {e}")

# --- Botones de Cálculo ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Calcular con Personal Requerido"):
        run_calculation(False)

with col2:
    if st.button("Calcular con Personal Actual"):
        run_calculation(True)
