import streamlit as st
import math

# --- Configuración de la Página de Streamlit ---
st.set_page_config(
    page_title="Calculadora de Personal para Turnos",
    page_icon="👥",
    layout="wide"
)

class CalculadoraPersonal:
    """
    Calculadora mejorada para determinar el personal requerido en operaciones por turnos.
    El cálculo se basa en la demanda total de turnos y la capacidad real de un operador.
    """

    def __init__(self, personal_actual, porcentaje_ausentismo, horas_objetivo_semana, horas_por_turno, personas_por_turno, cantidad_turnos_dia):
        self.personal_actual = personal_actual
        self.porcentaje_ausentismo = porcentaje_ausentismo
        self.horas_objetivo_semana = horas_objetivo_semana
        self.horas_por_turno = horas_por_turno
        self.personas_por_turno = personas_por_turno
        self.cantidad_turnos_dia = cantidad_turnos_dia
        self.dias_semana = 7

    def calcular_personal_requerido(self):
        """
        Calcula el personal total requerido basado en la carga de trabajo semanal.
        """
        # 1. Calcular la demanda total: ¿Cuántos puestos de trabajo hay que cubrir en la semana?
        turnos_a_cubrir_semana = self.personas_por_turno * self.cantidad_turnos_dia * self.dias_semana

        # 2. Calcular la oferta por persona: ¿Cuántos turnos puede cubrir una persona realmente?
        # Asegurarse de que las horas por turno no sean cero para evitar división por cero
        if self.horas_por_turno == 0:
            return 0, {}

        turnos_teoricos_por_persona = self.horas_objetivo_semana / self.horas_por_turno
        
        # Considerar el ausentismo para obtener la capacidad real
        factor_presencia = 1 - self.porcentaje_ausentismo
        turnos_reales_por_persona = turnos_teoricos_por_persona * factor_presencia

        # 3. Calcular el personal requerido
        # Si una persona no puede cubrir turnos, no se puede calcular el personal
        if turnos_reales_por_persona == 0:
             personal_requerido = float('inf') # Infinito si la gente no trabaja
        else:
            personal_requerido = math.ceil(turnos_a_cubrir_semana / turnos_reales_por_persona)
        
        # 4. Calcular métricas adicionales
        personal_adicional = max(0, personal_requerido - self.personal_actual)

        if personal_adicional > 0:
            razon_operadores = self.personal_actual / personal_adicional
        else:
            razon_operadores = float('inf')  # No se necesita personal adicional

        # Cobertura actual
        personal_total_disponible_real = self.personal_actual * turnos_reales_por_persona
        cobertura_actual = (personal_total_disponible_real / turnos_a_cubrir_semana) * 100 if turnos_a_cubrir_semana > 0 else 100.0


        resultados = {
            'turnos_a_cubrir_semana': turnos_a_cubrir_semana,
            'turnos_teoricos_por_persona': turnos_teoricos_por_persona,
            'turnos_reales_por_persona': turnos_reales_por_persona,
            'personal_requerido': personal_requerido,
            'personal_adicional': personal_adicional,
            'razon_operadores_adicional': razon_operadores,
            'cobertura_actual': cobertura_actual
        }

        return personal_requerido, resultados

def main():
    # --- Interfaz de Usuario ---
    st.title("👥 Calculadora de Dotación de Personal para Turnos")
    st.write("### Calcula el personal mínimo requerido para cubrir tu operación.")
    st.write("---")

    # --- Columnas para Inputs del Usuario ---
    col1, col2 = st.columns(2)

    with col1:
        st.write("#### ⚙️ Parámetros de la Operación")
        personas_por_turno = st.number_input(
            "👥 Personas requeridas por Turno:",
            min_value=1, max_value=500, value=4, step=1
        )
        cantidad_turnos_dia = st.number_input(
            "🔄 Cantidad de Turnos por Día:",
            min_value=1, max_value=5, value=2, step=1
        )
        horas_turno = st.number_input(
            "⏱️ Horas por Turno:",
            min_value=1.0, max_value=24.0, value=12.0, step=0.5
        )

    with col2:
        st.write("#### 🧑‍💼 Parámetros del Personal")
        personal_actual = st.number_input(
            "👤 Personal Actual (operadores):",
            min_value=1, max_value=1000, value=12, step=1
        )
        ausentismo_pct = st.slider(
            "📉 Porcentaje de Ausentismo (%):",
            min_value=0, max_value=50, value=15, step=1
        )
        horas_objetivo = st.number_input(
            "🎯 Horas Contratadas por Persona a la Semana:",
            min_value=20.0, max_value=60.0, value=44.0, step=0.5
        )

    # --- Cálculo ---
    calculadora = CalculadoraPersonal(
        personal_actual,
        ausentismo_pct / 100,
        horas_objetivo,
        horas_turno,
        personas_por_turno,
        cantidad_turnos_dia
    )
    personal_requerido, detalles = calculadora.calcular_personal_requerido()

    st.write("---")

    # --- Resultados Principales ---
    st.write("### 📈 Resultados Principales")
    res1, res2, res3, res4 = st.columns(4)

    res1.metric("👤 Personal Actual", personal_actual)
    
    adicional_text = f"+{detalles['personal_adicional']}" if detalles['personal_adicional'] > 0 else "✅ OK"
    res2.metric("👥 Personal Requerido", personal_requerido, adicional_text)
    
    res3.metric("➕ Adicional Necesario", detalles['personal_adicional'])

    cobertura = detalles.get('cobertura_actual', 0)
    res4.metric("📊 Cobertura Actual", f"{cobertura:.1f}%")

    # Mensaje principal de resultado
    if detalles['personal_adicional'] > 0:
        st.error(
            f"⚠️ **NECESITAS PERSONAL ADICIONAL:** Por cada **{detalles['razon_operadores_adicional']:.1f}** "
            f"operadores actuales, necesitas contratar **1 operador adicional** para cumplir el objetivo."
        )
    else:
        st.success("✅ **¡EXCELENTE!** Tu personal actual es suficiente para cubrir la operación.")

    st.write("---")

    # --- Análisis Detallado ---
    st.write("### 📋 Análisis Detallado del Cálculo")
    st.write("**Cálculos paso a paso:**")
    st.write(f"1. **Demanda Semanal:** Se deben cubrir **{detalles['turnos_a_cubrir_semana']:.0f} turnos** en total durante la semana.")
    st.write(f"   - _Cálculo: {personas_por_turno} personas/turno × {cantidad_turnos_dia} turnos/día × 7 días_")
    st.write(f"2. **Capacidad Teórica por Persona:** Cada persona está contratada para cubrir **{detalles['turnos_teoricos_por_persona']:.2f} turnos** por semana.")
    st.write(f"   - _Cálculo: {horas_objetivo} horas/semana ÷ {horas_turno} horas/turno_")
    st.write(f"3. **Capacidad Real por Persona (con {ausentismo_pct}% ausentismo):** Realísticamente, cada persona cubre **{detalles['turnos_reales_por_persona']:.2f} turnos** por semana.")
    st.write(f"4. **Cálculo Final de Personal Requerido:** **{personal_requerido} operadores**.")
    st.write(f"   - _Cálculo: {detalles['turnos_a_cubrir_semana']:.0f} turnos a cubrir ÷ {detalles['turnos_reales_por_persona']:.2f} turnos reales por persona_")
    
    st.write("---")

    # --- Análisis de Sensibilidad ---
    st.write("### 🔍 Análisis de Sensibilidad por Ausentismo")
    st.write("**¿Cómo afectan diferentes niveles de ausentismo al personal requerido?**")
    
    for aus in [0, 5, 10, 15, 20, 25, 30]:
        calc_temp = CalculadoraPersonal(personal_actual, aus / 100, horas_objetivo, horas_turno, personas_por_turno, cantidad_turnos_dia)
        req_temp, det_temp = calc_temp.calcular_personal_requerido()
        
        estado = "✅ OK" if det_temp['personal_adicional'] == 0 else f"❌ Falta(n) {det_temp['personal_adicional']}"
        
        if aus == ausentismo_pct:
            st.info(f"**👉 {aus}% - Personal Req: {req_temp} - Adicional: {det_temp['personal_adicional']} - {estado} ← TU CONFIGURACIÓN**")
        else:
            st.write(f"&nbsp;&nbsp;&nbsp;{aus}% - Personal Req: {req_temp} - Adicional: {det_temp['personal_adicional']} - {estado}")

    st.write("---")
    
    # --- Reporte de Texto ---
    st.write("### 📥 Reporte de Resultados")
    
    reporte = f"""REPORTE DE CÁLCULO DE PERSONAL PARA TURNOS
{'='*50}

CONFIGURACIÓN DE LA OPERACIÓN:
- Personas por turno: {personas_por_turno}
- Turnos por día: {cantidad_turnos_dia}
- Horas por turno: {horas_turno} horas
- Personal actual: {personal_actual} operadores
- Ausentismo proyectado: {ausentismo_pct}%
- Horas contratadas por semana: {horas_objetivo} horas

ANÁLISIS DE CARGA DE TRABAJO:
- Total de turnos a cubrir por semana: {detalles['turnos_a_cubrir_semana']:.0f}
- Turnos reales cubiertos por persona/semana: {detalles['turnos_reales_por_persona']:.2f}

RESULTADOS:
- Personal requerido para cobertura total: {personal_requerido} operadores
- Personal adicional necesario: {detalles['personal_adicional']} operadores
- Cobertura con el personal actual: {cobertura:.1f}%

RECOMENDACIÓN:
"""
    
    if detalles['personal_adicional'] > 0:
        reporte += f"⚠️ CONTRATAR {detalles['personal_adicional']} OPERADOR(ES) ADICIONAL(ES)\n"
        reporte += f"   Razón: 1 adicional por cada {detalles['razon_operadores_adicional']:.1f} actuales."
    else:
        reporte += "✅ EL PERSONAL ACTUAL ES SUFICIENTE PARA LA OPERACIÓN."
        
    st.text_area("Copia este reporte:", value=reporte, height=350)

if __name__ == "__main__":
    main()
