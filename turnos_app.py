import streamlit as st
import math

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Personal para Turnos",
    page_icon="👥",
    layout="wide"
)

class CalculadoraPersonal:
    """Calculadora para determinar personal requerido en turnos"""
    
    def __init__(self, personal_actual, porcentaje_ausentismo, horas_objetivo_semana=44.0, horas_por_turno=12.0):
        self.personal_actual = personal_actual
        self.porcentaje_ausentismo = porcentaje_ausentismo
        self.horas_objetivo_semana = horas_objetivo_semana
        self.horas_por_turno = horas_por_turno
        self.dias_semana = 7
    
    def calcular_horas_disponibles_por_persona(self):
        """Calcula las horas disponibles por persona considerando ausentismo"""
        horas_nominales_semana = self.horas_por_turno * self.dias_semana
        factor_presencia = 1 - self.porcentaje_ausentismo
        horas_reales_semana = horas_nominales_semana * factor_presencia
        return horas_reales_semana
    
    def calcular_personal_requerido(self):
        """Calcula el personal total requerido para cumplir con las horas objetivo"""
        # Horas reales disponibles por persona por semana
        horas_disponibles_persona = self.calcular_horas_disponibles_por_persona()
        
        # Factor de eficiencia (cuántas horas útiles por hora disponible)
        factor_eficiencia = self.horas_objetivo_semana / horas_disponibles_persona
        
        # Personal requerido (redondeado hacia arriba para garantizar cobertura)
        personal_requerido = math.ceil(self.personal_actual * factor_eficiencia)
        
        # Personal adicional necesario
        personal_adicional = max(0, personal_requerido - self.personal_actual)
        
        # Cálculo de la razón
        if personal_adicional > 0:
            razon_operadores = self.personal_actual / personal_adicional
        else:
            razon_operadores = float('inf')  # No se necesita personal adicional
        
        resultados = {
            'horas_nominales_semana': self.horas_por_turno * self.dias_semana,
            'horas_disponibles_persona': horas_disponibles_persona,
            'factor_eficiencia': factor_eficiencia,
            'personal_actual': self.personal_actual,
            'personal_requerido': personal_requerido,
            'personal_adicional': personal_adicional,
            'razon_operadores_adicional': razon_operadores,
            'cobertura_actual': (horas_disponibles_persona / self.horas_objetivo_semana) * 100
        }
        
        return personal_requerido, resultados

def main():
    # Título principal
    st.title("👥 Calculadora de Personal para Turnos")
    st.write("### Calcula el personal mínimo requerido para cumplir objetivos de horas semanales")
    st.write("---")
    
    # Inputs del usuario
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 📊 Configuración Básica")
        personal_actual = st.number_input(
            "👤 Personal Actual (operadores):",
            min_value=1,
            max_value=500,
            value=12,
            step=1
        )
        
        ausentismo_pct = st.slider(
            "📉 Porcentaje de Ausentismo (%):",
            min_value=0,
            max_value=50,
            value=15,
            step=1
        )
    
    with col2:
        st.write("#### ⏰ Configuración de Turnos")
        horas_objetivo = st.number_input(
            "🎯 Horas Objetivo por Semana:",
            min_value=20.0,
            max_value=60.0,
            value=44.0,
            step=0.5
        )
        
        horas_turno = st.number_input(
            "⏱️ Horas por Turno:",
            min_value=8.0,
            max_value=24.0,
            value=12.0,
            step=0.5
        )
    
    # Calculadora
    calculadora = CalculadoraPersonal(personal_actual, ausentismo_pct / 100, horas_objetivo, horas_turno)
    personal_requerido, detalles = calculadora.calcular_personal_requerido()
    
    st.write("---")
    
    # Métricas principales
    st.write("### 📈 Resultados Principales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👤 Personal Actual", personal_actual)
    
    with col2:
        adicional_text = f"+{detalles['personal_adicional']}" if detalles['personal_adicional'] > 0 else "✅ OK"
        st.metric("👥 Personal Requerido", personal_requerido, adicional_text)
    
    with col3:
        st.metric("➕ Adicional Necesario", detalles['personal_adicional'])
    
    with col4:
        cobertura = detalles['cobertura_actual']
        st.metric("📊 Cobertura Actual", f"{cobertura:.1f}%")
    
    # Mensaje principal
    if detalles['personal_adicional'] > 0:
        st.error(
            f"⚠️ **NECESITAS PERSONAL ADICIONAL:** Por cada {detalles['razon_operadores_adicional']:.1f} "
            f"operadores actuales necesitas **1 operador adicional** para cumplir el objetivo."
        )
    else:
        st.success("✅ **¡EXCELENTE!** Tu personal actual es suficiente para cumplir con el objetivo de horas.")
    
    st.write("---")
    
    # Resultados detallados
    st.write("### 📋 Análisis Detallado")
    
    # Crear tabla manualmente
    st.write("**Cálculos paso a paso:**")
    st.write(f"• Horas nominales por semana por persona: **{detalles['horas_nominales_semana']:.0f} horas**")
    st.write(f"• Horas reales (con {ausentismo_pct}% ausentismo): **{detalles['horas_disponibles_persona']:.1f} horas**")
    st.write(f"• Horas objetivo requeridas: **{horas_objetivo:.1f} horas**")
    st.write(f"• Gap de horas por persona: **{max(0, horas_objetivo - detalles['horas_disponibles_persona']):.1f} horas**")
    st.write(f"• Factor de eficiencia necesario: **{detalles['factor_eficiencia']:.3f}**")
    st.write(f"• Personal mínimo requerido: **{personal_requerido} operadores**")
    
    # Gráfico simple
    st.write("### 📊 Comparación Visual")
    actual_bar = "█" * personal_actual + f" {personal_actual}"
    requerido_bar = "█" * personal_requerido + f" {personal_requerido}"
    
    st.code(f"""Personal Actual:   {actual_bar}
Personal Requerido: {requerido_bar}""")
    
    st.write("---")
    
    # Análisis de sensibilidad
    st.write("### 🔍 Análisis de Sensibilidad por Ausentismo")
    
    st.write("**¿Cómo afectan diferentes niveles de ausentismo?**")
    
    for aus in [0, 5, 10, 15, 20, 25, 30]:
        calc_temp = CalculadoraPersonal(personal_actual, aus / 100, horas_objetivo, horas_turno)
        req_temp, det_temp = calc_temp.calcular_personal_requerido()
        
        estado = "✅ OK" if det_temp['personal_adicional'] == 0 else f"❌ Falta {det_temp['personal_adicional']}"
        razon = f"1:{det_temp['razon_operadores_adicional']:.1f}" if det_temp['personal_adicional'] > 0 else "Suficiente"
        
        # Destacar la configuración actual
        if aus == ausentismo_pct:
            st.write(f"**👉 {aus}% - Personal Req: {req_temp} - Adicional: {det_temp['personal_adicional']} - Razón: {razon} - {estado} ← TU CONFIGURACIÓN**")
        else:
            st.write(f"   {aus}% - Personal Req: {req_temp} - Adicional: {det_temp['personal_adicional']} - Razón: {razon} - {estado}")
    
    st.write("---")
    
    # Recomendaciones
    st.write("### 💡 Recomendaciones")
    
    if detalles['personal_adicional'] > 0:
        st.warning(f"""
**Acción Recomendada: CONTRATAR PERSONAL**

1. **Contrata {detalles['personal_adicional']} operadores adicionales** para cumplir el objetivo
2. **Razón de contratación:** 1 adicional por cada {detalles['razon_operadores_adicional']:.1f} actuales
3. **Alternativa:** Reduce el ausentismo para evitar contrataciones
        """)
    else:
        st.success(f"""
**¡Felicitaciones! Tu dotación actual es adecuada**

✅ No necesitas contratar personal adicional  
✅ Tu personal actual puede manejar la carga de trabajo  
✅ Tienes un margen de seguridad del {cobertura-100:.1f}%  
        """)
    
    # Generar reporte de texto
    st.write("### 📥 Reporte de Resultados")
    
    reporte = f"""REPORTE DE CÁLCULO DE PERSONAL PARA TURNOS
{'='*50}

CONFIGURACIÓN:
- Personal actual: {personal_actual} operadores
- Ausentismo: {ausentismo_pct}%
- Objetivo: {horas_objetivo} horas/semana/persona
- Horas por turno: {horas_turno} horas

ANÁLISIS:
- Horas nominales: {detalles['horas_nominales_semana']} horas/semana/persona
- Horas reales (con ausentismo): {detalles['horas_disponibles_persona']:.1f} horas/semana/persona
- Cobertura actual: {detalles['cobertura_actual']:.1f}%
- Factor de eficiencia necesario: {detalles['factor_eficiencia']:.3f}

RESULTADOS:
- Personal requerido: {personal_requerido} operadores
- Personal adicional necesario: {detalles['personal_adicional']} operadores

RECOMENDACIÓN:
"""
    
    if detalles['personal_adicional'] > 0:
        reporte += f"⚠️ CONTRATAR {detalles['personal_adicional']} OPERADORES ADICIONALES\n"
        reporte += f"   Razón: 1 adicional por cada {detalles['razon_operadores_adicional']:.1f} actuales"
    else:
        reporte += "✅ EL PERSONAL ACTUAL ES SUFICIENTE"
    
    st.text_area("Copia este reporte:", value=reporte, height=300)

if __name__ == "__main__":
    main()
