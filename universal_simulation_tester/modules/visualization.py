"""
Módulo de Visualização e Gráficos

Fornece visualizações interativas e estáticas para:
- Dashboard principal
- Gráficos detalhados de cada teste
- Mapas de calor para anisotropia
- Espectros de potência
- Histogramas e diagramas de dispersão
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class Visualization:
    """
    Classe para geração de visualizações científicas.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.theme = self.config.get('theme', 'dark')
        self.colors = self.config.get('color_palette', {
            'primary': '#00ff88',
            'secondary': '#00ccff',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'success': '#00ff88'
        })
    
    def get_suspicion_color(self, score: float) -> str:
        """Retorna cor baseada no índice de suspeita."""
        if score < 30:
            return self.colors['success']
        elif score < 70:
            return self.colors['warning']
        else:
            return self.colors['danger']
    
    def get_suspicion_label(self, score: float) -> str:
        """Retorna rótulo baseado no índice de suspeita."""
        if score < 30:
            return "Sem Anomalias Significativas"
        elif score < 70:
            return "Padrões Intrigantes Detectados"
        else:
            return "Anomalias Significativas Encontradas"
    
    def create_radar_chart_data(self, results: Dict) -> Dict:
        """
        Prepara dados para gráfico radar dos testes.
        
        Args:
            results: Dicionário com resultados dos testes
            
        Returns:
            Dados formatados para gráfico radar
        """
        labels = []
        scores = []
        colors = []
        
        for test_name, result in results.items():
            labels.append(result.test_name[:20])
            scores.append(result.anomaly_score)
            colors.append(self.get_suspicion_color(result.anomaly_score))
        
        return {
            'labels': labels,
            'scores': scores,
            'colors': colors,
            'max_score': 100
        }
    
    def generate_result_summary_html(self, results: Dict, overall_score: float) -> str:
        """
        Gera resumo HTML dos resultados.
        
        Args:
            results: Resultados dos testes
            overall_score: Índice agregado de suspeita
            
        Returns:
            String HTML formatada
        """
        color = self.get_suspicion_color(overall_score)
        label = self.get_suspicion_label(overall_score)
        
        html = f"""
        <div style="padding: 20px; font-family: sans-serif;">
            <h2 style="color: {color};">Índice de Suspeita Especulativa</h2>
            <div style="font-size: 48px; color: {color}; font-weight: bold;">
                {overall_score:.1f}%
            </div>
            <p style="font-size: 18px;">{label}</p>
            
            <h3>Resultados por Teste:</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #333; color: white;">
                    <th style="padding: 10px; text-align: left;">Teste</th>
                    <th style="padding: 10px;">Score</th>
                    <th style="padding: 10px;">Status</th>
                </tr>
        """
        
        for test_name, result in results.items():
            row_color = self.get_suspicion_color(result.anomaly_score)
            status = "⚠️ Anomalia" if result.anomaly_detected else "✓ Normal"
            html += f"""
                <tr style="border-bottom: 1px solid #555;">
                    <td style="padding: 10px;">{result.test_name}</td>
                    <td style="padding: 10px; text-align: center; color: {row_color};">
                        {result.anomaly_score:.1f}
                    </td>
                    <td style="padding: 10px; text-align: center;">{status}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #222; 
                        border-left: 4px solid #ffaa00;">
                <strong>⚠️ Lembrete Importante:</strong> Este índice é puramente 
                especulativo e não representa uma medição científica real de 
                probabilidade de simulação. Anomalias estatísticas podem ter 
                inúmeras explicações naturais e convencionais.
            </div>
        </div>
        """
        
        return html
    
    def create_plotly_config(self) -> Dict:
        """Retorna configuração para gráficos Plotly."""
        return {
            'displayModeBar': True,
            'responsive': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'locale': 'pt-BR'
        }
