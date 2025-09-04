import streamlit as st
import math
import pandas as pd
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

def crear_grafico_barras_simple(personal_actual, personal_requerido):
    """Crea un gráfico de barras simple usando caracteres"""
    max_val = max(personal_actual, personal_requerido)
    escala = 30 / max_val  # Normalizar a 30 caracteres máximo
    
    actual_bar = "█" * int(personal_actual * escala)
    requerido_bar = "█" * int(personal_requerido * escala)
    
    return f"""
```
Personal Actual   [{personal_actual:2d}] {actual_bar}
Personal Requerido[{personal_requerido:2d}] {requerido_bar}
```
"""

def main():
    # Título principal
    st.title("👥 Calculadora de Personal para Turnos")
    st.markdown("### Calcula el personal mínimo requerido para cumplir objetivos de horas semanales")
    st.markdown("---")
    
    # Layout en columnas para los inputs
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.subheader("📊 Configuración Básica")
        personal_actual = st.number_input(
            "👤 Personal Actual (operadores):",
            min_value=1,
            max_value=500,
            value=12,
            step=1,
            help="Número actual de operadores disponibles"
        )
        
        ausentismo_pct = st.slider(
            "📉 Porcentaje de Ausentismo (%):",
            min_value=0,
            max_value=50,
            value=15,
            step=1,
            help="Porcentaje promedio de ausentismo del personal"
        )
    
    with col_input2:
        st.subheader("⏰ Configuración de Turnos")
        horas_objetivo = st.number_input(
            "🎯 Horas Objetivo por Semana:",
            min_value=20.0,
            max_value=60.0,
            value=44.0,
            step=0.5,
            help="Promedio de horas que debe trabajar cada operador por semana"
        )
        
        horas_turno = st.number_input(
            "⏱️ Horas por Turno:",
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
    
    st.markdown("---")
    
    # Métricas principales
    st.subheader("📈 Resultados Principales")
    col1, col2, col3, col4 = st.columns(4)
    
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
            delta=f"+{detalles['personal_adicional']}" if detalles['personal_adicional'] > 0 else "✅ OK",
            delta_color="inverse" if detalles['personal_adicional'] > 0 else "normal"
        )
    
    with col3:
        st.metric(
            "➕ Adicional Necesario",
            f"{detalles['personal_adicional']}",
            help="Personal adicional que necesitas contratar"
        )
    
    with col4:
        cobertura = detalles['cobertura_actual']
        st.metric(
            "📊 Cobertura Actual",
            f"{cobertura:.1f}%",
            delta=f"{cobertura-100:.1f}pp" if cobertura != 100 else "Perfecto",
            delta_color="normal" if cobertura >= 100 else "inverse"
        )
    
    # Razón de personal - Destacado
    if detalles['personal_adicional'] > 0:
        st.error(
            f"⚠️ **NECESITAS PERSONAL ADICIONAL:** Por cada {detalles['razon_operadores_adicional']:.1f} "
            f"operadores actuales necesitas **1 operador adicional** para cumplir el objetivo."
        )
    else:
        st.success("✅ **¡EXCELENTE!** Tu personal actual es suficiente para cumplir con el objetivo de horas.")
    
    st.markdown("---")
    
    # Resultados detallados
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.subheader("📋 Análisis Detallado")
        
        # Tabla de resultados
        resultados_data = {
            'Concepto': [
                'Horas Nominales/Semana/Persona',
                'Horas Reales (con ausentismo)',
                'Horas Objetivo Requeridas',
                'Gap de Horas',
                'Factor de Eficiencia Necesario',
                'Personal Actual',
                'Personal Requerido (mínimo)',
                'Personal Adicional Necesario'
            ],
            'Valor': [
                f"{detalles['horas_nominales_semana']:.0f} horas",
                f"{detalles['horas_disponibles_persona']:.1f} horas",
                f"{horas_objetivo:.1f} horas",
                f"{horas_objetivo - detalles['horas_disponibles_persona']:.1f} horas",
                f"{detalles['factor_eficiencia']:.3f}",
                f"{personal_actual} operadores",
                f"{personal_requerido} operadores",
                f"{detalles['personal_adicional']} operadores"
            ],
            'Estado': [
                '📊',
                '📉' if detalles['horas_disponibles_persona'] < horas_objetivo else '📈',
                '🎯',
                '❌' if horas_objetivo > detalles['horas_disponibles_persona'] else '✅',
                '⚠️' if detalles['factor_eficiencia'] > 1 else '✅',
                '👤',
                '👥',
                '➕' if detalles['personal_adicional'] > 0 else '✅'
            ]
        }
        
        resultados_df = pd.DataFrame(resultados_data)
        st.dataframe(resultados_df, use_container_width=True, hide_index=True)
        
    with col_right:
        st.subheader("📊 Comparación Visual")
        
        # Gráfico simple con caracteres
        st.code(crear_grafico_barras_simple(personal_actual, personal_requerido))
        
        # Información adicional
        st.info(f"""
        **Resumen Ejecutivo:**
        
        • Con {ausentismo_pct}% de ausentismo
        • Cada persona trabaja {detalles['horas_disponibles_persona']:.1f}h reales/semana
        • Objetivo: {horas_objetivo}h/semana
        • Déficit: {max(0, horas_objetivo - detalles['horas_disponibles_persona']):.1f}h por persona
        """)
    
    st.markdown("---")
    
    # Análisis de sensibilidad
    st.subheader("🔍 Análisis de Sensibilidad por Ausentismo")
    
    # Crear datos para el análisis
    ausentismos = list(range(0, 31, 5))  # 0% a 30% en pasos de 5%
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
            'Ausentismo (%)': f"{aus}%",
            'Personal Requerido': req_temp,
            'Personal Adicional': det_temp['personal_adicional'],
            'Razón (actual:adicional)': f"1:{det_temp['razon_operadores_adicional']:.1f}" if det_temp['personal_adicional'] > 0 else "Suficiente",
            'Estado': '✅ OK' if det_temp['personal_adicional'] == 0 else f"❌ Falta {det_temp['personal_adicional']}"
        })
    
    df_sensibilidad = pd.DataFrame(datos_sensibilidad)
    
    # Destacar la fila actual
    current_row = df_sensibilidad[df_sensibilidad['Ausentismo (%)'] == f"{ausentismo_pct}%"].index
    if len(current_row) > 0:
        st.info(f"👆 Tu configuración actual está resaltada: {ausentismo_pct}% de ausentismo")
    
    st.dataframe(
        df_sensibilidad, 
        use_container_width=True, 
        hide_index=True
    )
    
    # Recomendaciones
    st.markdown("---")
    st.sub
