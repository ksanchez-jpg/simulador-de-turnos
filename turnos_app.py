import streamlit as st
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import Tuple

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Personal para Turnos",
    page_icon="👥",
    layout="wide"
)

@dataclass
class ParametrosTurnos:
    """Parámetros para el cálculo de personal requerido"""
    personal_actual: int
    porcentaje_ausentismo: float  # Como decimal (ej: 0.15 para 15%)
    horas_objetivo_semana: float = 44.0
    horas_por_turno: float = 12.0
    dias_semana: int = 7
    semanas_calculo: int = 3

class CalculadoraPersonal:
    """Calculadora para determinar personal requerido en turnos"""
    
    def __init__(self, parametros: ParametrosTurnos):
        self.parametros = parametros
    
    def calcular_horas_disponibles_por_persona(self) -> float:
        """Calcula las horas disponibles por persona considerando ausentismo"""
        horas_nominales_semana = self.parametros.horas_por_turno * self.parametros.dias_semana
        factor_presencia = 1 - self.parametros.porcentaje_ausentismo
        horas_reales_semana = horas_nominales_semana * factor_presencia
        return horas_reales_semana
    
    def calcular_personal_requerido(self) -> Tuple[int, dict]:
        """
        Calcula el personal total requerido para cumplir con las 44 horas promedio
        
        Returns:
            Tuple[int, dict]: (personal_requerido, detalles_calculo)
        """
        # Horas reales disponibles por persona por semana
        horas_disponibles_persona = self.calcular_horas_disponibles_por_persona()
        
        # Factor de eficiencia (cuántas horas útiles por hora disponible)
        factor_eficiencia = self.parametros.horas_objetivo_semana / horas_disponibles_persona
        
        # Personal requerido (redondeado hacia arriba para garantizar cobertura)
        personal_requerido = math.ceil(self.parametros.personal_actual * factor_eficiencia)
        
        # Personal adicional necesario
        personal_adicional = max(0, personal_requerido - self.parametros.personal_actual)
        
        # Cálculo de la razón
        if personal_adicional > 0:
            razon_operadores = self.parametros.personal_actual / personal_adicional
        else:
            razon_operadores = float('inf')  # No se necesita personal adicional
        
        detalles = {
            'horas_nominales_semana': self.parametros.horas_por_turno * self.parametros.dias_semana,
            'horas_disponibles_persona': horas_disponibles_persona,
            'factor_eficiencia': factor_eficiencia,
            'personal_actual': self.parametros.personal_actual,
            'personal_requerido': personal_requerido,
            'personal_adicional': personal_adicional,
            'razon_operadores_adicional': razon_operadores,
            'horas_promedio_logradas': horas_disponibles_persona,
            'cobertura_actual': (horas_disponibles_persona / self.parametros.horas_objetivo_semana) * 100
        }
        
        return personal_requerido, detalles

def main():
    # Título principal
    st.title("👥 Calculadora de Personal para Turnos")
    st.markdown("---")
    
    # Sidebar para parámetros
    st.sidebar.header("📊 Parámetros de Configuración")
    
    # Inputs del usuario
    personal_actual = st.sidebar.number_input(
        "Personal Actual (operadores):",
        min_value=1,
        max_value=500,
        value=12,
        step=1,
        help="Número actual de operadores disponibles"
    )
    
    ausentismo_pct = st.sidebar.slider(
        "Porcentaje de Ausentismo (%):",
        min_value=0,
        max_value=50,
        value=15,
        step=1,
        help="Porcentaje promedio de ausentismo del personal"
    )
    
    horas_objetivo = st.sidebar.number_input(
        "Horas Objetivo por Semana:",
        min_value=20.0,
        max_value=60.0,
        value=44.0,
        step=0.5,
        help="Promedio de horas que debe trabajar cada operador por semana"
    )
    
    horas_turno = st.sidebar.number_input(
        "Horas por Turno:",
        min_value=8.0,
        max_value=24.0,
        value=12.0,
        step=0.5,
        help="Duración de cada turno en horas"
    )
    
    # Crear parámetros
    parametros = ParametrosTurnos(
        personal_actual=personal_actual,
        porcentaje_ausentismo=ausentismo_pct / 100,
        horas_objetivo_semana=horas_objetivo,
        horas_por_turno=horas_turno
    )
    
    # Calculadora
    calculadora = CalculadoraPersonal(parametros)
    personal_requerido, detalles = calculadora.calcular_personal_requerido()
    
    # Layout principal en columnas
    col1, col2, col3 = st.columns([2, 2, 2])
    
    # Métricas principales
    with col1:
        st.metric(
            "👤 Personal Actual",
            f"{personal_actual}",
            help="Operadores disponibles actualmente"
        )
    
    with col2:
        st.metric(
            "👥 Personal Requerido",
            f"{personal_requerido}",
            delta=f"{detalles['personal_adicional']} adicional" if detalles['personal_adicional'] > 0 else "✅ Suficiente",
            delta_color="inverse" if detalles['personal_adicional'] > 0 else "normal"
        )
    
    with col3:
        cobertura = detalles['cobertura_actual']
        st.metric(
            "📈 Cobertura Actual",
            f"{cobertura:.1f}%",
            delta=f"{cobertura-100:.1f}%" if cobertura != 100 else "Perfecto",
            delta_color="normal" if cobertura >= 100 else "inverse"
        )
    
    st.markdown("---")
    
    # Resultados detallados
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.subheader("📋 Análisis Detallado")
        
        # Tabla de resultados
        resultados_df = pd.DataFrame({
            'Concepto': [
                'Horas Nominales/Semana',
                'Horas Reales (con ausentismo)',
                'Horas Objetivo',
                'Factor de Eficiencia',
                'Personal Actual',
                'Personal Requerido',
                'Personal Adicional'
            ],
            'Valor': [
                f"{detalles['horas_nominales_semana']:.0f} hrs",
                f"{detalles['horas_disponibles_persona']:.1f} hrs",
                f"{horas_objetivo:.1f} hrs",
                f"{detalles['factor_eficiencia']:.3f}",
                f"{personal_actual} operadores",
                f"{personal_requerido} operadores",
                f"{detalles['personal_adicional']} operadores"
            ]
        })
        
        st.dataframe(resultados_df, use_container_width=True, hide_index=True)
        
        # Razón de personal adicional
        if detalles['personal_adicional'] > 0:
            st.info(
                f"📊 **Razón de Personal:** Por cada {detalles['razon_operadores_adicional']:.1f} "
                f"operadores actuales se necesita **1 operador adicional**"
            )
        else:
            st.success("✅ **El personal actual es suficiente** para cumplir con el objetivo de horas")
    
    with col_right:
        st.subheader("📊 Visualización")
        
        # Gráfico de comparación
        fig_bar = go.Figure(data=[
            go.Bar(
                name='Actual',
                x=['Personal'],
                y=[personal_actual],
                marker_color='lightblue',
                text=[f"{personal_actual}"],
                textposition='auto',
            ),
            go.Bar(
                name='Requerido',
                x=['Personal'],
                y=[personal_requerido],
                marker_color='orange',
                text=[f"{personal_requerido}"],
                textposition='auto',
            )
        ])
        
        fig_bar.update_layout(
            title="Personal: Actual vs Requerido",
            yaxis_title="Número de Operadores",
            height=400,
            barmode='group'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Análisis de sensibilidad
    st.subheader("🔍 Análisis de Sensibilidad")
    
    with st.expander("Ver análisis por diferentes niveles de ausentismo"):
        # Crear datos para el análisis
        ausentismos = range(5, 31, 2)  # 5% a 30% en pasos de 2%
        datos_sensibilidad = []
        
        for aus in ausentismos:
            params_temp = ParametrosTurnos(
                personal_actual=personal_actual,
                porcentaje_ausentismo=aus / 100,
                horas_objetivo_semana=horas_objetivo,
                horas_por_turno=horas_turno
            )
            calc_temp = CalculadoraPersonal(params_temp)
            req_temp, det_temp = calc_temp.calcular_personal_requerido()
            
            datos_sensibilidad.append({
                'Ausentismo (%)': aus,
                'Personal Requerido': req_temp,
                'Personal Adicional': det_temp['personal_adicional'],
                'Razón': f"1:{det_temp['razon_operadores_adicional']:.1f}" if det_temp['personal_adicional'] > 0 else "Suficiente"
            })
        
        df_sensibilidad = pd.DataFrame(datos_sensibilidad)
        
        # Mostrar tabla
        st.dataframe(df_sensibilidad, use_container_width=True, hide_index=True)
        
        # Gráfico de sensibilidad
        fig_sens = px.line(
            df_sensibilidad,
            x='Ausentismo (%)',
            y='Personal Requerido',
            title='Personal Requerido vs. Nivel de Ausentismo',
            markers=True
        )
        
        fig_sens.add_hline(
            y=personal_actual,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Personal Actual ({personal_actual})"
        )
        
        fig_sens.update_layout(height=400)
        st.plotly_chart(fig_sens, use_container_width=True)
    
    # Exportar resultados
    st.markdown("---")
    st.subheader("📥 Exportar Resultados")
    
    # Crear reporte para exportar
    reporte_export = f"""REPORTE DE CÁLCULO DE PERSONAL PARA TURNOS
===========================================

PARÁMETROS:
- Personal actual: {personal_actual} operadores
- Ausentismo: {ausentismo_pct}%
- Objetivo: {horas_objetivo} horas/semana
- Horas por turno: {horas_turno} horas

RESULTADOS:
- Horas nominales por semana: {detalles['horas_nominales_semana']} horas
- Horas reales (con ausentismo): {detalles['horas_disponibles_persona']:.1f} horas
- Personal requerido: {personal_requerido} operadores
- Personal adicional: {detalles['personal_adicional']} operadores
- Cobertura actual: {detalles['cobertura_actual']:.1f}%

"""
    
    if detalles['personal_adicional'] > 0:
        reporte_export += f"RAZÓN: Por cada {detalles['razon_operadores_adicional']:.1f} operadores se necesita 1 adicional"
    else:
        reporte_export += "ESTADO: El personal actual es suficiente"
    
    st.download_button(
        label="📄 Descargar Reporte",
        data=reporte_export,
        file_name=f"reporte_personal_turnos_{personal_actual}ops_{ausentismo_pct}aus.txt",
        mime="text/plain"
    )

if __name__ == "__main__":
    main()
