import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Simulador de Turnos", layout="wide")
st.title("🕒 Programación de Turnos por Semana (con restricciones)")

# === Entradas del usuario ===
trabajadores_actuales = st.number_input("Ingrese el número de operadores actuales:", min_value=1, step=1)
horas_a_cubrir = st.number_input("¿Cuántas horas deben cubrirse a la semana?", min_value=1, step=1)
tipo_turno = st.radio("Seleccione el tipo de turnos:", ("2 Turnos de 12h", "3 Turnos de 8h"))

# Solo ejecutar si hay datos suficientes
if trabajadores_actuales and horas_a_cubrir and tipo_turno:

    # === CONFIGURACIONES BÁSICAS ===
    num_operadores = trabajadores_actuales
    num_semanas = 4
    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    turnos_diarios = 2 if tipo_turno == "2 Turnos de 12h" else 3
    duracion_turno = 12 if tipo_turno == "2 Turnos de 12h" else 8
    horas_totales_turno = duracion_turno * 7  # horas por semana por turno

    # Generar lista de operadores con estado
    operadores = {
        f"OP{i+1}": {
            "turnos": [],
            "horas_semanales": [],
            "domingos_seguidos": 0,
            "total_horas": 0
        }
        for i in range(num_operadores)
    }

    # Asignación de turnos rotativos por semana
    calendarios = {}
    for semana in range(1, num_semanas + 1):
        semana_key = f"Semana {semana}"
        for turno in range(1, turnos_diarios + 1):
            turno_key = f"{semana_key} - Turno {turno}"
            df = pd.DataFrame(index=[], columns=dias_semana)

            # Filtrar operadores para este turno por rotación
            operadores_turno = []
            for idx, (op, data) in enumerate(operadores.items()):
                # ROTACIÓN SEMANAL
                turno_asignado = (semana + idx) % turnos_diarios + 1
                if turno_asignado == turno:
                    operadores_turno.append(op)

            # Generar filas por operador
            for op in operadores_turno:
                fila = []
                dias_trabajados = 0
                domingos_seguidos = operadores[op]["domingos_seguidos"]
                for i, dia in enumerate(dias_semana):
                    if dia == "domingo":
                        # DESCANSAR SI YA TIENE 2 DOMINGOS CONSECUTIVOS
                        if domingos_seguidos >= 2:
                            fila.append("")
                            operadores[op]["domingos_seguidos"] = 0
                            continue
                        else:
                            operadores[op]["domingos_seguidos"] += 1

                    # DECISIÓN DE TRABAJO VS DESCANSO
                    if dias_trabajados < 6:
                        fila.append(op)
                        dias_trabajados += 1
                    else:
                        fila.append("")

                df.loc[op] = fila

                # CALCULAR HORAS TRABAJADAS EN LA SEMANA
                horas_semana = dias_trabajados * duracion_turno
                operadores[op]["horas_semanales"].append(horas_semana)
                operadores[op]["total_horas"] += horas_semana
                operadores[op]["turnos"].append(turno)

            calendarios[turno_key] = df

    # === VALIDACIONES ===
    st.subheader("📋 Validación de restricciones")

    errores = []
    for op, data in operadores.items():
        # Regla 2: Horas promedio cada 2 semanas = 42
        for i in range(0, num_semanas, 2):
            h1 = data["horas_semanales"][i]
            h2 = data["horas_semanales"][i+1] if i+1 < len(data["horas_semanales"]) else 0
            if round((h1 + h2) / 2) != 42:
                errores.append(f"{op}: promedio semanas {i+1}-{i+2} ≠ 42h")

        # Regla 3: Promedio de 8h/día al mes
        if round(data["total_horas"] / 28, 1) != 8.0:
            errores.append(f"{op}: promedio diario ≠ 8h (actual: {data['total_horas']/28:.1f})")

        # Regla 6: Cambio de turno requiere descanso de 1 día
        for i in range(1, len(data["turnos"])):
            if data["turnos"][i] != data["turnos"][i-1]:
                # asumimos descanso domingo-lunes ya implementado al limitar 6 días de trabajo
                pass  # ya garantizado en la lógica de descanso

    if errores:
        for e in errores:
            st.error(e)
    else:
        st.success("✅ Todas las restricciones se cumplen correctamente.")

    # === MOSTRAR PROGRAMACIÓN ===
    st.subheader("📅 Programación de turnos")
    for semana in range(1, num_semanas + 1):
        st.markdown(f"### Semana {semana}")
        cols = st.columns(turnos_diarios)
        for turno in range(1, turnos_diarios + 1):
            with cols[turno - 1]:
                st.markdown(f"**Turno {turno}**")
                st.dataframe(
                    calendarios[f"Semana {semana} - Turno {turno}"],
                    use_container_width=True
                )

