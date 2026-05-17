"""
Testes Unitários para o Universal Simulation Hypothesis Tester

Este módulo contém testes unitários para validar cada componente do sistema.
Execute com: pytest tests/test_all.py -v
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.data_loader import DataLoader
from modules.simulation_tests import SimulationTests, TestResult
from modules.statistical_analysis import StatisticalAnalysis
from modules.visualization import Visualization
from modules.report_generator import ReportGenerator
from modules.educational import EducationalContent


class TestDataLoader:
    """Testes para o módulo DataLoader."""
    
    def test_init(self):
        """Testa inicialização do DataLoader."""
        dl = DataLoader()
        assert dl.data is None
        assert dl.metadata == {}
    
    def test_generate_simulated_data_cmb(self):
        """Testa geração de dados CMB simulados."""
        dl = DataLoader()
        data = dl.generate_simulated_data('cosmic_microwave', num_samples=1000, seed=42)
        
        assert len(data) == 1000
        assert 'theta' in data.columns
        assert 'phi' in data.columns
        assert 'temperature_K' in data.columns
        assert 'delta_T_T' in data.columns
        
        # Verifica faixa de valores
        assert data['theta'].min() >= 0
        assert data['theta'].max() <= np.pi
        assert data['phi'].min() >= 0
        assert data['phi'].max() <= 2 * np.pi
    
    def test_generate_simulated_data_quantum(self):
        """Testa geração de dados quânticos simulados."""
        dl = DataLoader()
        data = dl.generate_simulated_data('quantum_particles', num_samples=500, seed=42)
        
        assert len(data) == 500
        assert 'angle_a_rad' in data.columns
        assert 'angle_b_rad' in data.columns
        assert 'result_a' in data.columns
        assert 'result_b' in data.columns
        assert 'correlation_expected' in data.columns
        
        # Resultados devem ser +1 ou -1
        assert set(data['result_a'].unique()).issubset({-1, 1})
        assert set(data['result_b'].unique()).issubset({-1, 1})
    
    def test_generate_simulated_data_cosmic_rays(self):
        """Testa geração de dados de raios cósmicos."""
        dl = DataLoader()
        data = dl.generate_simulated_data('cosmic_rays', num_samples=300, seed=42)
        
        assert len(data) == 300
        assert 'energy_eV' in data.columns
        assert 'right_ascension_deg' in data.columns
        assert 'declination_deg' in data.columns
        
        # Energias devem estar na faixa esperada
        assert data['energy_eV'].min() > 0
        assert data['energy_eV'].max() <= 1e20
    
    def test_generate_simulated_data_constants(self):
        """Testa geração de constantes físicas simuladas."""
        dl = DataLoader()
        data = dl.generate_simulated_data('constants', num_samples=200, seed=42)
        
        assert len(data) == 200
        assert 'fine_structure' in data.columns
        assert 'proton_electron_ratio' in data.columns
        assert 'gravitational' in data.columns
    
    def test_validate_data_empty(self):
        """Testa validação de dados vazios."""
        dl = DataLoader()
        is_valid, errors = dl.validate_data()
        
        assert not is_valid
        assert any("Nenhum dado" in err for err in errors)
    
    def test_validate_data_with_data(self):
        """Testa validação de dados válidos."""
        dl = DataLoader()
        dl.data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        is_valid, errors = dl.validate_data()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_preprocess_data_normalize(self):
        """Testa normalização de dados."""
        dl = DataLoader()
        dl.data = pd.DataFrame({'x': [1, 2, 3, 4, 5]})
        processed = dl.preprocess_data(normalize=True, remove_outliers=False)
        
        assert 'x_normalized' in processed.columns
        assert abs(processed['x_normalized'].mean()) < 0.001  # Média ~0


class TestSimulationTests:
    """Testes para o motor de testes científicos."""
    
    def test_init(self):
        """Testa inicialização do SimulationTests."""
        st = SimulationTests()
        assert st.results == {}
    
    def test_run_all_tests(self):
        """Testa execução de todos os testes."""
        st = SimulationTests()
        dl = DataLoader()
        data = dl.generate_simulated_data('cosmic_microwave', num_samples=1000, seed=42)
        
        results = st.run_all_tests(data)
        
        # Deve ter 6 testes
        assert len(results) == 6
        
        # Cada resultado deve ser um TestResult
        for key, result in results.items():
            assert isinstance(result, TestResult)
            assert hasattr(result, 'test_name')
            assert hasattr(result, 'anomaly_detected')
            assert hasattr(result, 'significance')
    
    def test_calculate_overall_suspicion_index(self):
        """Testa cálculo do índice de suspeita."""
        st = SimulationTests()
        dl = DataLoader()
        data = dl.generate_simulated_data('constants', num_samples=500, seed=42)
        
        st.run_all_tests(data)
        score = st.calculate_overall_suspicion_index()
        
        # Score deve estar entre 0 e 100
        assert 0 <= score <= 100
    
    def test_spacetime_discretization_test(self):
        """Testa especificamente o teste de discretização."""
        st = SimulationTests()
        dl = DataLoader()
        data = dl.generate_simulated_data('cosmic_microwave', num_samples=500, seed=42)
        
        result = st.test_spacetime_discretization(data)
        
        assert result.test_name == "Discretização do Espaço-Tempo"
        assert isinstance(result.anomaly_score, (int, float))  # Pode ser int ou float
        assert 0 <= result.anomaly_score <= 100
    
    def test_rounding_errors_test(self):
        """Testa especificamente o teste de erros de arredondamento."""
        st = SimulationTests()
        dl = DataLoader()
        data = dl.generate_simulated_data('constants', num_samples=300, seed=42)
        
        result = st.test_rounding_errors(data)
        
        assert result.test_name == "Erros de Arredondamento Cósmico"
        assert isinstance(result.details, dict)
    
    def test_nonlocal_correlations_test(self):
        """Testa especificamente o teste de correlações não-locais."""
        st = SimulationTests()
        dl = DataLoader()
        data = dl.generate_simulated_data('quantum_particles', num_samples=1000, seed=42)
        
        result = st.test_nonlocal_correlations(data)
        
        assert result.test_name == "Correlações Não-Locais Anômalas"
        assert 'bell_parameter' in result.details or 'tsirelson_limit' in str(result.details)


class TestStatisticalAnalysis:
    """Testes para análise estatística."""
    
    def test_init(self):
        """Testa inicialização do StatisticalAnalysis."""
        sa = StatisticalAnalysis()
        assert sa.significance_level == 0.05
        assert sa.confidence_level == 0.95
    
    def test_calculate_significance(self):
        """Testa cálculo de significância."""
        sa = StatisticalAnalysis()
        observed = np.random.normal(5.1, 1.0, 100)
        expected = 5.0
        
        result = sa.calculate_significance(observed, expected, test_type='t')
        
        assert hasattr(result, 'p_value')
        assert hasattr(result, 'confidence_interval')
        assert 0 <= result.p_value <= 1
    
    def test_bonferroni_correction(self):
        """Testa correção de Bonferroni."""
        sa = StatisticalAnalysis()
        p_values = [0.01, 0.03, 0.05, 0.1, 0.5]
        
        corrected = sa.bonferroni_correction(p_values)
        
        assert len(corrected) == len(p_values)
        # Valores corrigidos devem ser maiores ou iguais aos originais
        for orig, corr in zip(p_values, corrected):
            assert corr >= orig
    
    def test_fdr_correction(self):
        """Testa correção FDR (Benjamini-Hochberg)."""
        sa = StatisticalAnalysis()
        p_values = [0.01, 0.03, 0.05, 0.1, 0.5]
        
        corrected = sa.fdr_correction(p_values)
        
        assert len(corrected) == len(p_values)
        # Todos os valores devem estar entre 0 e 1
        assert all(0 <= p <= 1 for p in corrected)
    
    def test_detect_outliers(self):
        """Testa detecção de outliers."""
        sa = StatisticalAnalysis()
        data = np.array([1, 2, 3, 4, 5, 100])  # 100 é outlier
        
        outliers = sa.detect_outliers_sigma(data, n_sigma=2.0)
        
        assert sum(outliers) >= 1  # Pelo menos um outlier detectado
        assert outliers[-1]  # O último valor (100) deve ser outlier
    
    def test_warn_about_phacking(self):
        """Testa geração de aviso sobre p-hacking."""
        sa = StatisticalAnalysis()
        warning = sa.warn_about_phacking(num_tests=10)
        
        assert "P-HACKING" in warning.upper() or "VIÉS" in warning.upper()
        assert "10" in warning  # Deve mencionar o número de testes


class TestVisualization:
    """Testes para visualização."""
    
    def test_init(self):
        """Testa inicialização do Visualization."""
        viz = Visualization()
        assert hasattr(viz, 'colors')
        assert hasattr(viz, 'theme')
    
    def test_get_suspicion_color(self):
        """Testa obtenção de cor baseada no score."""
        viz = Visualization()
        
        assert viz.get_suspicion_color(10) == viz.colors['success']  # Verde
        assert viz.get_suspicion_color(50) == viz.colors['warning']  # Amarelo
        assert viz.get_suspicion_color(80) == viz.colors['danger']   # Vermelho
    
    def test_get_suspicion_label(self):
        """Testa rótulos de suspeita."""
        viz = Visualization()
        
        assert "Sem" in viz.get_suspicion_label(10) or "Normal" in viz.get_suspicion_label(10)
        assert "Intrigantes" in viz.get_suspicion_label(50) or "Padrões" in viz.get_suspicion_label(50)
        assert "Anomalias" in viz.get_suspicion_label(80)
    
    def test_create_radar_chart_data(self):
        """Testa preparação de dados para gráfico radar."""
        viz = Visualization()
        
        # Cria resultados mock
        results = {
            'test1': type('obj', (object,), {
                'test_name': 'Teste 1',
                'anomaly_score': 25.0,
                'anomaly_detected': False
            })(),
            'test2': type('obj', (object,), {
                'test_name': 'Teste 2',
                'anomaly_score': 75.0,
                'anomaly_detected': True
            })()
        }
        
        data = viz.create_radar_chart_data(results)
        
        assert 'labels' in data
        assert 'scores' in data
        assert 'colors' in data
        assert len(data['labels']) == 2
        assert len(data['scores']) == 2


class TestReportGenerator:
    """Testes para geração de relatórios."""
    
    def test_init(self):
        """Testa inicialização do ReportGenerator."""
        rg = ReportGenerator()
        assert rg.export_dir.exists()
    
    def test_generate_summary_report(self):
        """Testa geração de relatório de resumo."""
        rg = ReportGenerator()
        
        # Cria resultados mock
        results = {
            'spacetime_discretization': type('obj', (object,), {
                'test_name': 'Discretização do Espaço-Tempo',
                'anomaly_detected': False,
                'anomaly_score': 15.0,
                'significance': 0.45,
                'effect_size': 0.1,
                'theoretical_basis': 'Base teórica de exemplo',
                'limitations': ['Limitação 1'],
                'warnings': []
            })()
        }
        
        report = rg.generate_summary_report(results, overall_score=22.5, data_metadata={
            'source': 'simulated',
            'format': 'csv',
            'num_rows': 1000,
            'num_cols': 5
        })
        
        assert "RELATÓRIO" in report
        assert "22.5" in report
        assert "DISCRETIZAÇÃO" in report.upper() or "ESPAÇO-TEMPO" in report.upper()
        assert "O QUE REALMENTE PODEMOS CONCLUIR" in report
    
    def test_export_to_json(self, tmp_path):
        """Testa exportação para JSON."""
        rg = ReportGenerator()
        
        results = {
            'test1': type('obj', (object,), {
                'test_name': 'Teste JSON',
                'anomaly_detected': True,
                'anomaly_score': 65.0,
                'significance': 0.02,
                'effect_size': 0.3,
                'details': {'key': 'value'},
                'warnings': ['Aviso de teste']
            })()
        }
        
        filepath = tmp_path / "test_output.json"
        rg.export_to_json(results, str(filepath))
        
        assert filepath.exists()
    
    def test_export_to_csv(self, tmp_path):
        """Testa exportação para CSV."""
        rg = ReportGenerator()
        
        results = {
            'test1': type('obj', (object,), {
                'test_name': 'Teste CSV',
                'anomaly_detected': False,
                'anomaly_score': 30.0,
                'significance': 0.15,
                'effect_size': 0.05,
                'details': {},
                'warnings': []
            })()
        }
        
        filepath = tmp_path / "test_output.csv"
        rg.export_to_csv(results, str(filepath))
        
        assert filepath.exists()
    
    def test_generate_latex(self):
        """Testa geração de código LaTeX."""
        rg = ReportGenerator()
        
        results = {
            'test1': type('obj', (object,), {
                'test_name': 'Teste LaTeX',
                'anomaly_detected': False,
                'anomaly_score': 10.0,
                'significance': 0.5,
                'effect_size': 0.01,
                'details': {},
                'warnings': []
            })()
        }
        
        latex = rg.generate_latex(results, overall_score=10.0)
        
        assert "\\documentclass" in latex
        assert "\\section" in latex
        assert "10.0" in latex


class TestEducationalContent:
    """Testes para conteúdo educacional."""
    
    def test_init(self):
        """Testa inicialização do EducationalContent."""
        ec = EducationalContent()
        
        assert len(ec.test_explanations) == 6
        assert len(ec.physicist_biographies) > 0
        assert len(ec.myths_and_facts) > 0
        assert len(ec.glossary) > 0
    
    def test_get_test_explanation(self):
        """Testa obtenção de explicação de teste."""
        ec = EducationalContent()
        
        explanation = ec.get_test_explanation('spacetime_discretization')
        
        assert 'title' in explanation
        assert 'simple_explanation' in explanation
        assert 'Discretização' in explanation['title']
    
    def test_glossary_terms(self):
        """Testa termos do glossário."""
        ec = EducationalContent()
        
        glossary = ec.get_all_glossary_terms()
        
        assert 'Anomalia Estatística' in glossary or 'p-value' in glossary
        assert len(glossary) >= 10
    
    def test_physicist_biographies(self):
        """Testa biografias de físicos."""
        ec = EducationalContent()
        
        bell = ec.get_physicist_by_name('Bell')
        
        assert 'name' in bell
        assert 'contribution' in bell
        assert 'Bell' in bell['name']
    
    def test_myths_and_facts(self):
        """Testa seção mitos e verdades."""
        ec = EducationalContent()
        
        fact = ec.get_random_fact()
        
        assert 'myth' in fact
        assert 'fact' in fact


class TestIntegration:
    """Testes de integração do fluxo completo."""
    
    def test_full_workflow(self):
        """Testa fluxo completo: dados -> testes -> resultados -> relatório."""
        # 1. Carregar dados
        dl = DataLoader()
        data = dl.generate_simulated_data('cosmic_microwave', num_samples=2000, seed=42)
        
        # 2. Executar testes
        st = SimulationTests()
        results = st.run_all_tests(data)
        
        # 3. Calcular score
        score = st.calculate_overall_suspicion_index()
        
        # 4. Gerar relatório
        rg = ReportGenerator()
        report = rg.generate_summary_report(results, score, dl.get_metadata())
        
        # Validações
        assert len(results) == 6
        assert 0 <= score <= 100
        assert "RELATÓRIO" in report
        assert f"{score:.1f}" in report
    
    def test_different_data_types(self):
        """Testa diferentes tipos de dados simulados."""
        st = SimulationTests()
        dl = DataLoader()
        
        data_types = ['cosmic_microwave', 'quantum_particles', 'cosmic_rays', 'constants']
        
        for dtype in data_types:
            data = dl.generate_simulated_data(dtype, num_samples=500, seed=42)
            results = st.run_all_tests(data)
            
            assert len(results) == 6
            
            # Limpa resultados para próximo teste
            st.results = {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
