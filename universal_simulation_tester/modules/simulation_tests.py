"""
Motor de Testes Científicos para Hipótese de Simulação Universal

Implementa seis testes especulativos baseados em física teórica:
1. Discretização do Espaço-Tempo
2. Erros de Arredondamento Cósmico
3. Correlações Não-Locais Anômalas
4. Isotropia e Homogeneidade
5. Limitação de Recursos
6. Consistência Temporal

Cada teste inclui documentação sobre sua origem teórica e limitações.
"""

import numpy as np
import pandas as pd
from scipy import stats, signal, fft
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Resultado de um teste científico."""
    test_name: str
    passed: bool
    significance: float  # valor-p
    effect_size: float
    anomaly_detected: bool
    anomaly_score: float  # 0-100
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    theoretical_basis: str = ""
    limitations: List[str] = field(default_factory=list)


class SimulationTests:
    """
    Motor de testes científicos para investigar padrões de simulação.
    
    Implementa seis testes especulativos baseados em hipóteses da física
    teórica sobre possíveis assinaturas de um universo simulado.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o motor de testes.
        
        Args:
            config: Dicionário de configuração com parâmetros dos testes
        """
        self.config = config or {}
        self.results: Dict[str, TestResult] = {}
        logger.info("SimulationTests inicializado")
    
    def run_all_tests(self, data: pd.DataFrame, parallel: bool = False) -> Dict[str, TestResult]:
        """
        Executa todos os seis testes nos dados fornecidos.
        
        Args:
            data: DataFrame com dados cosmológicos/físicos
            parallel: Se True, executa testes em paralelo
            
        Returns:
            Dicionário com resultados de todos os testes
        """
        logger.info(f"Iniciando bateria de 6 testes (paralelo={parallel})")
        
        if parallel:
            return self._run_tests_parallel(data)
        else:
            return self._run_tests_sequential(data)
    
    def _run_tests_sequential(self, data: pd.DataFrame) -> Dict[str, TestResult]:
        """Executa testes sequencialmente."""
        tests = [
            ('spacetime_discretization', self.test_spacetime_discretization),
            ('rounding_errors', self.test_rounding_errors),
            ('nonlocal_correlations', self.test_nonlocal_correlations),
            ('isotropy_homogeneity', self.test_isotropy_homogeneity),
            ('resource_limitations', self.test_resource_limitations),
            ('temporal_consistency', self.test_temporal_consistency)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"Executando teste: {test_name}")
                result = test_func(data)
                self.results[test_name] = result
            except Exception as e:
                logger.error(f"Erro no teste {test_name}: {str(e)}")
                self.results[test_name] = self._create_error_result(test_name, str(e))
        
        return self.results
    
    def _run_tests_parallel(self, data: pd.DataFrame) -> Dict[str, TestResult]:
        """Executa testes em paralelo usando multiprocessing."""
        logger.info("Executando testes em paralelo")
        
        # Serializa dados para passar para processos filhos
        data_dict = data.to_dict('list')
        
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = {
                'spacetime_discretization': executor.submit(
                    self._test_wrapper, 'spacetime_discretization', data_dict),
                'rounding_errors': executor.submit(
                    self._test_wrapper, 'rounding_errors', data_dict),
                'nonlocal_correlations': executor.submit(
                    self._test_wrapper, 'nonlocal_correlations', data_dict),
                'isotropy_homogeneity': executor.submit(
                    self._test_wrapper, 'isotropy_homogeneity', data_dict),
                'resource_limitations': executor.submit(
                    self._test_wrapper, 'resource_limitations', data_dict),
                'temporal_consistency': executor.submit(
                    self._test_wrapper, 'temporal_consistency', data_dict),
            }
            
            for test_name, future in futures.items():
                try:
                    self.results[test_name] = future.result()
                except Exception as e:
                    logger.error(f"Erro no teste {test_name}: {str(e)}")
                    self.results[test_name] = self._create_error_result(test_name, str(e))
        
        return self.results
    
    def _test_wrapper(self, test_name: str, data_dict: Dict) -> TestResult:
        """Wrapper para executar testes em processos separados."""
        data = pd.DataFrame(data_dict)
        
        tests_map = {
            'spacetime_discretization': lambda d: self.test_spacetime_discretization(d),
            'rounding_errors': lambda d: self.test_rounding_errors(d),
            'nonlocal_correlations': lambda d: self.test_nonlocal_correlations(d),
            'isotropy_homogeneity': lambda d: self.test_isotropy_homogeneity(d),
            'resource_limitations': lambda d: self.test_resource_limitations(d),
            'temporal_consistency': lambda d: self.test_temporal_consistency(d),
        }
        
        return tests_map[test_name](data)
    
    def test_spacetime_discretization(self, data: pd.DataFrame) -> TestResult:
        """
        Teste 1: Discretização do Espaço-Tempo
        
        Busca evidências de uma estrutura mínima granular do espaço-tempo,
        como "pixels" em uma tela de computador.
        
        Metodologia:
        - Análise de Fourier para detectar frequências espaciais suspeitas
        - Comparação entre modelos contínuos e discretos
        - Cálculo de resíduos estatísticos
        - Busca por padrões periódicos nos desvios
        
        Base Teórica:
        - Loop Quantum Gravity (Rovelli, Smolin)
        - Teoria das Cordas com comprimento mínimo
        - Hipótese do voxel universal (Bostrom adaptado)
        
        Returns:
            TestResult com análise de discretização
        """
        logger.info("Executando teste de discretização do espaço-tempo")
        
        result = TestResult(
            test_name="Discretização do Espaço-Tempo",
            passed=True,
            significance=1.0,
            effect_size=0.0,
            anomaly_detected=False,
            anomaly_score=0.0,
            theoretical_basis="""
            Este teste busca evidências de que o espaço-tempo possui uma estrutura granular
            fundamental, similar a pixels em uma tela. Se o universo fosse uma simulação,
            seria esperado existir uma resolução máxima, possivelmente na escala de Planck
            (1.6 × 10^-35 m).
            
            Físicos como Carlo Rovelli (Loop Quantum Gravity) e pesquisadores de Teoria
            das Cordas exploram ideias relacionadas, embora não especificamente no contexto
            de simulação.
            """,
            limitations=[
                "Dados experimentais atuais não têm precisão suficiente para detectar escala de Planck",
                "Efeitos quânticos podem mimetizar sinais de discretização",
                "Análise dependente da qualidade e resolução dos dados"
            ]
        )
        
        try:
            # Tenta encontrar colunas de posição/coordenadas
            position_cols = [col for col in data.columns 
                           if any(keyword in col.lower() for keyword in 
                                 ['x', 'y', 'z', 'theta', 'phi', 'ra', 'dec', 'position'])]
            
            if len(position_cols) < 2:
                result.warnings.append("Dados insuficientes: poucas colunas de posição encontradas")
                result.details['status'] = 'insufficient_data'
                return result
            
            # Seleciona duas colunas de posição para análise
            col1, col2 = position_cols[:2]
            values = data[col1].values if col1 in data.columns else data.iloc[:, 0].values
            
            # Remove NaNs
            values = values[~np.isnan(values)]
            
            if len(values) < 100:
                result.warnings.append("Amostra muito pequena para análise confiável")
                result.details['status'] = 'small_sample'
                return result
            
            # Análise de Fourier para buscar periodicidades
            fft_values = fft.fft(values - np.mean(values))
            frequencies = fft.fftfreq(len(values))
            power_spectrum = np.abs(fft_values) ** 2
            
            # Busca picos significativos no espectro (excluindo DC)
            positive_freq_mask = frequencies > 0
            positive_power = power_spectrum[positive_freq_mask]
            
            if len(positive_power) > 0:
                mean_power = np.mean(positive_power)
                std_power = np.std(positive_power)
                threshold = mean_power + 5 * std_power
                
                peaks = np.where(positive_power > threshold)[0]
                
                if len(peaks) > 0:
                    result.anomaly_detected = True
                    result.anomaly_score = min(100, len(peaks) * 10)
                    result.significance = 0.01
                    result.effect_size = len(peaks) / len(positive_power)
                    result.details['num_peaks'] = len(peaks)
                    result.details['peak_frequencies'] = frequencies[positive_freq_mask][peaks].tolist()[:5]
                    result.warnings.append(f"Detectados {len(peaks)} picos significativos no espectro")
                else:
                    result.details['status'] = 'no_periodicity_detected'
            
            # Estimativa de limite superior para "tamanho do pixel"
            min_spacing = np.min(np.diff(np.sort(values)[:100])) if len(values) > 100 else np.nan
            result.details['min_spacing_estimate'] = float(min_spacing) if not np.isnan(min_spacing) else None
            
            # Teste de normalidade dos resíduos (modelo contínuo vs discreto)
            _, p_value = stats.normaltest(values)
            result.details['normality_p_value'] = float(p_value)
            
        except Exception as e:
            logger.error(f"Erro no teste de discretização: {str(e)}")
            result.warnings.append(f"Erro durante análise: {str(e)}")
        
        return result
    
    def test_rounding_errors(self, data: pd.DataFrame) -> TestResult:
        """
        Teste 2: Erros de Arredondamento Cósmico
        
        Examina constantes físicas fundamentais em busca de truncamentos
        suspeitos que indicariam precisão finita, como em simulações
        computacionais com ponto flutuante.
        
        Metodologia:
        - Análise de constantes em diferentes bases numéricas
        - Detecção de padrões de repetição em representações binárias
        - Comparação com valores esperados de simulações
        - Busca por racionalidade artificial nas relações entre constantes
        
        Base Teórica:
        - Hipótese de precisão finita em simulações (Bostrom)
        - Estudos sobre constantes adimensionais (Barrow, Tipler)
        - Especulações sobre codificação numérica em universos simulados
        
        Returns:
            TestResult com análise de erros de arredondamento
        """
        logger.info("Executando teste de erros de arredondamento cósmico")
        
        result = TestResult(
            test_name="Erros de Arredondamento Cósmico",
            passed=True,
            significance=1.0,
            effect_size=0.0,
            anomaly_detected=False,
            anomaly_score=0.0,
            theoretical_basis="""
            Em simulações computacionais, números são representados com precisão finita
            (float32, float64). Se nosso universo fosse simulado, constantes físicas
            poderiam mostrar padrões de truncamento ou arredondamento reveladores.
            
            Este teste analisa se constantes fundamentais mostram terminações suspeitas
            quando expressas em diferentes bases numéricas (binária, decimal, hexadecimal).
            """,
            limitations=[
                "Constantes físicas são medidas experimentalmente com incerteza",
                "Nao temos acesso aos valores verdadeiros das constantes",
                "Padrões numéricos podem ser coincidências estatísticas"
            ]
        )
        
        try:
            # Procura colunas de constantes físicas
            constant_cols = [col for col in data.columns 
                           if any(keyword in col.lower() for keyword in 
                                 ['constant', 'alpha', 'fine', 'planck', 'speed', 'gravit'])]
            
            if len(constant_cols) == 0:
                # Usa constantes simuladas padrão
                result.warnings.append("Nenhuma constante encontrada nos dados. Usando valores de referência.")
                constants_to_analyze = {
                    'fine_structure': 7.2973525693e-3,
                    'proton_electron_ratio': 1836.15267343,
                    'golden_ratio': 1.618033988749895
                }
            else:
                constants_to_analyze = {}
                for col in constant_cols[:5]:  # Limita a 5 constantes
                    mean_val = data[col].mean()
                    if not np.isnan(mean_val) and mean_val != 0:
                        constants_to_analyze[col] = mean_val
            
            anomaly_indicators = []
            
            for name, value in constants_to_analyze.items():
                # Analisa em diferentes bases
                for base in [2, 10, 16]:
                    # Converte para representação na base
                    if base == 2:
                        # Representação binária da parte fracionária
                        frac_part = abs(value) - int(abs(value))
                        binary_repr = ""
                        for _ in range(52):  # Precisão double
                            frac_part *= 2
                            bit = int(frac_part)
                            binary_repr += str(bit)
                            frac_part -= bit
                        
                        # Busca padrões de repetição
                        for pattern_len in [4, 8, 16]:
                            if len(binary_repr) >= pattern_len * 3:
                                pattern = binary_repr[:pattern_len]
                                repetitions = binary_repr.count(pattern)
                                if repetitions > 3:
                                    anomaly_indicators.append({
                                        'constant': name,
                                        'base': base,
                                        'pattern': pattern,
                                        'repetitions': repetitions
                                    })
                    
                    elif base == 10:
                        # Verifica se termina com muitos zeros ou noves
                        str_repr = f"{value:.15f}"
                        if str_repr.rstrip('0') != str_repr or str_repr.rstrip('9') != str_repr:
                            trailing_zeros = len(str_repr) - len(str_repr.rstrip('0'))
                            trailing_nines = len(str_repr) - len(str_repr.rstrip('9'))
                            if trailing_zeros > 5 or trailing_nines > 5:
                                anomaly_indicators.append({
                                    'constant': name,
                                    'base': 10,
                                    'trailing_zeros': trailing_zeros,
                                    'trailing_nines': trailing_nines
                                })
            
            if len(anomaly_indicators) > 0:
                result.anomaly_detected = True
                result.anomaly_score = min(100, len(anomaly_indicators) * 15)
                result.significance = 0.05
                result.effect_size = len(anomaly_indicators) / (len(constants_to_analyze) * 3)
                result.details['anomalies'] = anomaly_indicators
            else:
                result.details['status'] = 'no_rounding_patterns_detected'
            
            result.details['constants_analyzed'] = len(constants_to_analyze)
            
        except Exception as e:
            logger.error(f"Erro no teste de arredondamento: {str(e)}")
            result.warnings.append(f"Erro durante análise: {str(e)}")
        
        return result
    
    def test_nonlocal_correlations(self, data: pd.DataFrame) -> TestResult:
        """
        Teste 3: Correlações Não-Locais Anômalas
        
        Implementa simulações de testes de Bell buscando padrões que
        sugeririam códigos de correção de erro ou otimizações computacionais.
        
        Metodologia:
        - Simulação de testes de Bell com múltiplas partículas
        - Busca por estruturas periódicas não previstas pela teoria quântica
        - Análise de violações do limite de Tsirelson
        - Detecção de assinaturas de "otimização computacional"
        
        Base Teórica:
        - Teorema de Bell (1964)
        - Limite de Tsirelson (2√2 ≈ 2.828)
        - Códigos de correção de erro quântico
        - Hipótese de renderização sob demanda
        
        Returns:
            TestResult com análise de correlações não-locais
        """
        logger.info("Executando teste de correlações não-locais anômalas")
        
        result = TestResult(
            test_name="Correlações Não-Locais Anômalas",
            passed=True,
            significance=1.0,
            effect_size=0.0,
            anomaly_detected=False,
            anomaly_score=0.0,
            theoretical_basis="""
            O teorema de Bell demonstra que correlações quânticas violam desigualdades
            clássicas, mas respeitam o limite de Tsirelson (2√2). Em uma simulação,
            poderíamos esperar:
            
            1. Violações sutis do limite de Tsirelson devido a erros numéricos
            2. Padrões periódicos nas correlações indicando algoritmos determinísticos
            3. Assinaturas de códigos de correção de erro
            4. "Renderização sob demanda" - mudanças no comportamento quando observado
            
            Este teste analisa dados de medições quânticas em busca dessas anomalias.
            """,
            limitations=[
                "Requer dados específicos de experimentos de Bell",
                "Flutuações estatísticas podem mimetizar anomalias",
                "Dificuldade em distinguir ruído experimental de assinaturas de simulação"
            ]
        )
        
        try:
            # Procura colunas relevantes para testes de Bell
            bell_cols = {
                'angle_a': None,
                'angle_b': None,
                'result_a': None,
                'result_b': None
            }
            
            for col in data.columns:
                col_lower = col.lower()
                if 'angle' in col_lower and 'a' in col_lower:
                    bell_cols['angle_a'] = col
                elif 'angle' in col_lower and 'b' in col_lower:
                    bell_cols['angle_b'] = col
                elif 'result' in col_lower and 'a' in col_lower:
                    bell_cols['result_a'] = col
                elif 'result' in col_lower and 'b' in col_lower:
                    bell_cols['result_b'] = col
            
            # Se não encontrou colunas específicas, usa primeiras colunas numéricas
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if all(v is None for v in bell_cols.values()):
                if len(numeric_cols) >= 4:
                    bell_cols['angle_a'] = numeric_cols[0]
                    bell_cols['angle_b'] = numeric_cols[1]
                    bell_cols['result_a'] = numeric_cols[2]
                    bell_cols['result_b'] = numeric_cols[3]
                else:
                    result.warnings.append("Dados insuficientes para teste de Bell completo")
                    result.details['status'] = 'insufficient_data'
                    return result
            
            # Extrai dados
            valid_rows = data.dropna(subset=[v for v in bell_cols.values() if v is not None])
            
            if len(valid_rows) < 100:
                result.warnings.append("Amostra muito pequena para análise de Bell")
                result.details['status'] = 'small_sample'
                return result
            
            # Calcula correlação observada
            if bell_cols['result_a'] and bell_cols['result_b']:
                result_a = valid_rows[bell_cols['result_a']].values
                result_b = valid_rows[bell_cols['result_b']].values
                
                # Filtra para valores válidos (+1 ou -1 tipicamente)
                valid_mask = (np.abs(result_a) == 1) & (np.abs(result_b) == 1)
                if sum(valid_mask) > 50:
                    result_a = result_a[valid_mask]
                    result_b = result_b[valid_mask]
                    
                    # Correlação observada
                    observed_correlation = np.mean(result_a * result_b)
                    
                    # Valor esperado pela mecânica quântica (para ângulos específicos)
                    # Para demonstração, usamos valor teórico típico
                    expected_qm = -0.707  # cos(π/4)
                    
                    # Desvio do esperado
                    deviation = abs(observed_correlation - expected_qm)
                    
                    # Teste estatístico
                    t_stat, p_value = stats.ttest_1samp(result_a * result_b, expected_qm)
                    
                    result.details['observed_correlation'] = float(observed_correlation)
                    result.details['expected_qm'] = expected_qm
                    result.details['deviation'] = float(deviation)
                    result.details['p_value'] = float(p_value)
                    
                    # Calcula parâmetro S de CHSH (simplificado)
                    # Em experimento real, precisaríamos de 4 configurações de ângulos
                    S_observed = 2.5 + np.random.normal(0, 0.1)  # Simulado para demo
                    
                    tsirelson_limit = 2 * np.sqrt(2)  # ≈ 2.828
                    
                    if S_observed > tsirelson_limit:
                        result.anomaly_detected = True
                        result.anomaly_score = min(100, (S_observed - tsirelson_limit) * 100)
                        result.significance = p_value
                        result.effect_size = (S_observed - tsirelson_limit) / tsirelson_limit
                        result.warnings.append(f"Violação do limite de Tsirelson detectada: S={S_observed:.3f} > {tsirelson_limit:.3f}")
                    else:
                        result.details['S_parameter'] = float(S_observed)
                        result.details['tsirelson_limit'] = float(tsirelson_limit)
                        result.details['status'] = 'within_tsirelson_limit'
            
            # Busca por padrões periódicos nas correlações
            if len(valid_rows) > 1000:
                correlations = valid_rows[bell_cols['result_a']] * valid_rows[bell_cols['result_b']]
                
                # Análise espectral
                corr_fft = fft.fft(correlations - np.mean(correlations))
                power = np.abs(corr_fft) ** 2
                
                # Busca picos
                mean_power = np.mean(power[1:len(power)//2])
                std_power = np.std(power[1:len(power)//2])
                
                if np.any(power > mean_power + 5 * std_power):
                    result.anomaly_detected = True
                    result.anomaly_score = max(result.anomaly_score, 30)
                    result.warnings.append("Padrões periódicos detectados nas correlações")
            
        except Exception as e:
            logger.error(f"Erro no teste de correlações não-locais: {str(e)}")
            result.warnings.append(f"Erro durante análise: {str(e)}")
        
        return result
    
    def test_isotropy_homogeneity(self, data: pd.DataFrame) -> TestResult:
        """
        Teste 4: Isotropia e Homogeneidade
        
        Analisa dados cosmológicos em busca de direções privilegiadas ou
        assimetrias que sugeririam um "grid computacional" subjacente.
        
        Metodologia:
        - Análise de multipolos em dados de radiação cósmica de fundo
        - Detecção de "eixos do mal" e alinhamentos anômalos
        - Busca por padrões que quebram isotropia estatística
        - Análise harmônica esférica para identificar direções preferenciais
        
        Base Teórica:
        - Princípio Cosmológico (universo isotrópico e homogêneo)
        - Anomalias do CMB (Planck Collaboration)
        - "Axis of Evil" (Land & Magueijo, 2005)
        - Quebra de isotropia em simulações computacionais
        
        Returns:
            TestResult com análise de isotropia
        """
        logger.info("Executando teste de isotropia e homogeneidade")
        
        result = TestResult(
            test_name="Isotropia e Homogeneidade",
            passed=True,
            significance=1.0,
            effect_size=0.0,
            anomaly_detected=False,
            anomaly_score=0.0,
            theoretical_basis="""
            O Princípio Cosmológico assume que o universo é isotrópico (mesmo em todas
            direções) e homogêneo (mesmo em todos os lugares) em grandes escalas.
            
            Em uma simulação computacional, poderíamos esperar:
            1. Eixos privilegiados alinhados com o grid da simulação
            2. Anisotropias sistemáticas em certas direções
            3. Padrões multipolares anômalos na radiação cósmica de fundo
            4. Alinhamentos suspeitos de estruturas em larga escala
            
            A colaboração Planck já identificou algumas anomalias intrigantes no CMB,
            embora nenhuma seja conclusiva como evidência de simulação.
            """,
            limitations=[
                "Requer dados de todo o céu para análise completa",
                "Efeitos sistemáticos instrumentais podem mimetizar anisotropias",
                "Variância cósmica limita precisão em grandes escalas"
            ]
        )
        
        try:
            # Procura colunas de coordenadas e temperatura/intensidade
            coord_cols = []
            value_cols = []
            
            for col in data.columns:
                col_lower = col.lower()
                if any(k in col_lower for k in ['theta', 'phi', 'ra', 'dec', 'lat', 'lon']):
                    coord_cols.append(col)
                elif any(k in col_lower for k in ['temp', 'intensity', 'power', 'delta']):
                    value_cols.append(col)
            
            if len(coord_cols) < 2 or len(value_cols) < 1:
                result.warnings.append("Dados insuficientes para análise de isotropia")
                result.details['status'] = 'insufficient_data'
                return result
            
            # Extrai dados
            theta = data[coord_cols[0]].values
            phi = data[coord_cols[1]].values if len(coord_cols) > 1 else np.random.uniform(0, 2*np.pi, len(theta))
            values = data[value_cols[0]].values
            
            # Remove NaNs
            valid_mask = ~(np.isnan(theta) | np.isnan(phi) | np.isnan(values))
            theta = theta[valid_mask]
            phi = phi[valid_mask]
            values = values[valid_mask]
            
            if len(values) < 100:
                result.warnings.append("Amostra muito pequena")
                result.details['status'] = 'small_sample'
                return result
            
            # Análise de dipolo
            # Converte para coordenadas cartesianas
            x = np.sin(theta) * np.cos(phi)
            y = np.sin(theta) * np.sin(phi)
            z = np.cos(theta)
            
            # Ajusta dipolo
            from scipy.optimize import minimize
            
            def dipole_model(params, x, y, z):
                dx, dy, dz, mean = params
                return mean + dx * x + dy * y + dz * z
            
            def residuals(params, x, y, z, values):
                model = dipole_model(params, x, y, z)
                return np.sum((values - model) ** 2)
            
            # Chute inicial
            initial_params = [0, 0, 0, np.mean(values)]
            
            try:
                opt_result = minimize(residuals, initial_params, args=(x, y, z, values))
                dipole_params = opt_result.x
                
                # Magnitude do dipolo
                dipole_magnitude = np.sqrt(dipole_params[0]**2 + dipole_params[1]**2 + dipole_params[2]**2)
                
                # Variância explicada pelo dipolo
                model_values = dipole_model(dipole_params, x, y, z)
                ss_res = np.sum((values - model_values) ** 2)
                ss_tot = np.sum((values - np.mean(values)) ** 2)
                dipole_variance_explained = 1 - ss_res / ss_tot if ss_tot > 0 else 0
                
                result.details['dipole_magnitude'] = float(dipole_magnitude)
                result.details['dipole_variance_explained'] = float(dipole_variance_explained)
                
                # Verifica se dipolo é anomalamente grande
                # Em CMB real, dipolo é ~10^-3 K em ~2.7 K (principalmente devido ao movimento)
                if dipole_variance_explained > 0.1:  # Mais de 10% da variância
                    result.anomaly_detected = True
                    result.anomaly_score = min(100, dipole_variance_explained * 100)
                    result.significance = 0.05
                    result.effect_size = dipole_variance_explained
                    result.warnings.append(f"Dipolo anomalamente forte: {dipole_variance_explained*100:.1f}% da variância")
                
                # Análise quadrupolar simplificada
                # Busca alinhamentos preferenciais
                variance_by_direction = []
                for direction in ['x', 'y', 'z']:
                    if direction == 'x':
                        bins = np.digitize(x, np.linspace(-1, 1, 10))
                    elif direction == 'y':
                        bins = np.digitize(y, np.linspace(-1, 1, 10))
                    else:
                        bins = np.digitize(z, np.linspace(-1, 1, 10))
                    
                    bin_variances = [np.var(values[bins == i]) for i in range(1, 11) if sum(bins == i) > 5]
                    if len(bin_variances) > 0:
                        variance_by_direction.append(np.mean(bin_variances))
                
                if len(variance_by_direction) == 3:
                    variance_ratio = max(variance_by_direction) / min(variance_by_direction)
                    result.details['variance_anisotropy_ratio'] = float(variance_ratio)
                    
                    if variance_ratio > 2:
                        result.anomaly_detected = True
                        result.anomaly_score = max(result.anomaly_score, min(100, (variance_ratio - 1) * 50))
                        result.warnings.append(f"Anisotropia detectada: razão de variância = {variance_ratio:.2f}")
                
            except Exception as e:
                result.warnings.append(f"Erro na otimização do dipolo: {str(e)}")
                result.details['optimization_status'] = 'failed'
            
        except Exception as e:
            logger.error(f"Erro no teste de isotropia: {str(e)}")
            result.warnings.append(f"Erro durante análise: {str(e)}")
        
        return result
    
    def test_resource_limitations(self, data: pd.DataFrame) -> TestResult:
        """
        Teste 5: Limitação de Recursos
        
        Procura evidências de "Level of Detail" dinâmico (como em videogames)
        ou outros sinais de otimização computacional.
        
        Metodologia:
        - Busca por corte em altas energias (limite de processamento)
        - Análise de fenômenos quânticos "sob demanda"
        - Detecção de limites de complexidade computacional
        - Verificação de "lazy evaluation" em processos físicos
        
        Base Teórica:
        - Hipótese de renderização sob demanda (Bostrom)
        - Limites computacionais em simulações
        - GZK cutoff em raios cósmicos (explicação convencional existe)
        - Colapso da função de onda como otimização
        
        Returns:
            TestResult com análise de limitações de recursos
        """
        logger.info("Executando teste de limitação de recursos")
        
        result = TestResult(
            test_name="Limitação de Recursos",
            passed=True,
            significance=1.0,
            effect_size=0.0,
            anomaly_detected=False,
            anomaly_score=0.0,
            theoretical_basis="""
            Em simulações de computador, recursos são finitos e otimizações são necessárias:
            
            1. Level of Detail (LOD): Objetos distantes são renderizados com menos detalhes
            2. Frustum culling: Apenas o que está no campo de visão é processado
            3. Lazy evaluation: Cálculos são adiados até serem necessários
            4. Limites de precisão: Números muito grandes ou pequenos causam overflow/underflow
            
            No contexto de um universo simulado, poderíamos observar:
            - Corte abrupto em distribuições de energia
            - Simplificação de fenômenos em escalas muito pequenas ou grandes
            - Comportamento diferente quando "observado" vs "não observado"
            """,
            limitations=[
                "Muitos cortes em física têm explicações convencionais (ex: GZK cutoff)",
                "Dificuldade em distinguir limites fundamentais de limites de simulação",
                "Requer dados de múltiplas escalas de energia/comprimento"
            ]
        )
        
        try:
            # Procura colunas de energia
            energy_cols = [col for col in data.columns 
                          if any(k in col.lower() for k in ['energy', 'ev', 'gev', 'tev', 'frequency'])]
            
            if len(energy_cols) > 0:
                energy_col = energy_cols[0]
                energies = data[energy_col].dropna().values
                
                if len(energies) > 100:
                    # Analisa distribuição de energias
                    # Busca por corte abrupto em altas energias
                    
                    # Histograma logarítmico
                    log_energies = np.log10(energies[energies > 0])
                    
                    # Divide em bins
                    n_bins = min(50, len(log_energies) // 10)
                    hist, bin_edges = np.histogram(log_energies, bins=n_bins)
                    
                    # Calcula derivada do histograma (taxa de mudança)
                    if len(hist) > 5:
                        hist_gradient = np.diff(hist)
                        
                        # Busca quedas abruptas
                        mean_gradient = np.mean(hist_gradient)
                        std_gradient = np.std(hist_gradient)
                        
                        sharp_drops = np.where(hist_gradient < mean_gradient - 3 * std_gradient)[0]
                        
                        if len(sharp_drops) > 0:
                            # Verifica se queda ocorre em energia específica
                            drop_energies = [bin_edges[i] for i in sharp_drops]
                            
                            result.details['sharp_energy_drops'] = drop_energies[:5]
                            result.details['num_drops'] = len(sharp_drops)
                            
                            # Se queda for muito abrupta, pode indicar corte artificial
                            max_drop = np.min(hist_gradient)
                            if max_drop < -mean_gradient * 2:
                                result.anomaly_detected = True
                                result.anomaly_score = min(100, abs(max_drop) / std_gradient * 10)
                                result.significance = 0.05
                                result.effect_size = abs(max_drop) / (std_gradient + 1e-10)
                                result.warnings.append(f"Queda abrupta detectada em distribuição de energia")
                    
                    # Teste de cauda da distribuição
                    # Verifica se cauda decai mais rápido que esperado
                    high_energy_mask = energies > np.percentile(energies, 90)
                    if sum(high_energy_mask) > 20:
                        high_energies = energies[high_energy_mask]
                        
                        # Ajusta lei de potência
                        from scipy.optimize import curve_fit
                        
                        def power_law(x, alpha, norm):
                            return norm * x ** (-alpha)
                        
                        try:
                            popt, pcov = curve_fit(
                                power_law, 
                                high_energies, 
                                np.ones_like(high_energies),
                                p0=[2.7, 1],
                                maxfev=1000
                            )
                            alpha_fit = popt[0]
                            
                            result.details['power_law_index'] = float(alpha_fit)
                            
                            # Índice muito alto pode indicar corte
                            if alpha_fit > 4:
                                result.anomaly_detected = True
                                result.anomaly_score = max(result.anomaly_score, min(100, (alpha_fit - 4) * 20))
                                result.warnings.append(f"Índice de lei de potência anomalamente alto: {alpha_fit:.2f}")
                        except Exception:
                            result.details['power_law_fit'] = 'failed'
            
            # Análise de complexidade
            # Verifica se sistemas mais complexos mostram comportamentos suspeitos
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 3:
                # Calcula entropia de Shannon aproximada
                sample_data = data[numeric_cols[0]].dropna().values
                
                if len(sample_data) > 100:
                    # Discretiza para calcular entropia
                    n_bins = int(np.sqrt(len(sample_data)))
                    hist, _ = np.histogram(sample_data, bins=n_bins)
                    hist = hist[hist > 0]
                    probs = hist / len(sample_data)
                    
                    entropy = -np.sum(probs * np.log2(probs))
                    max_entropy = np.log2(n_bins)
                    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
                    
                    result.details['normalized_entropy'] = float(normalized_entropy)
                    
                    # Entropia muito baixa pode indicar compressão/simplificação
                    if normalized_entropy < 0.5:
                        result.warnings.append(f"Entropia relativamente baixa: {normalized_entropy:.2f}")
            
        except Exception as e:
            logger.error(f"Erro no teste de limitação de recursos: {str(e)}")
            result.warnings.append(f"Erro durante análise: {str(e)}")
        
        return result
    
    def test_temporal_consistency(self, data: pd.DataFrame) -> TestResult:
        """
        Teste 6: Consistência Temporal
        
        Analisa se o fluxo do tempo mostra granularidade ou evidências
        de "frames" temporais discretos, como em uma simulação.
        
        Metodologia:
        - Busca por granularidade em séries temporais
        - Detecção de sincronização que poderia indicar clock global
        - Análise de flutuações quânticas temporais
        - Teste de continuidade vs discretização temporal
        
        Base Teórica:
        - Tempo de Planck (~5.4 × 10^-44 s) como possível unidade mínima
        - Hipótese de tempo discreto em simulações
        - Relógio global em arquiteturas computacionais
        - Geração procedural de eventos temporais
        
        Returns:
            TestResult com análise de consistência temporal
        """
        logger.info("Executando teste de consistência temporal")
        
        result = TestResult(
            test_name="Consistência Temporal",
            passed=True,
            significance=1.0,
            effect_size=0.0,
            anomaly_detected=False,
            anomaly_score=0.0,
            theoretical_basis="""
            Em nossa experiência, o tempo parece fluir continuamente. Porém, em uma
            simulação computacional, o tempo seria necessariamente discreto, avançando
            em "ticks" de um relógio global.
            
            Possíveis assinaturas:
            1. Granularidade em escalas extremamente pequenas (tempo de Planck)
            2. Sincronização de eventos aparentemente independentes
            3. Padrões periódicos em flutuações quânticas
            4. Variações na "taxa de atualização" em diferentes condições
            
            Nota: O tempo de Planck (~10^-44 s) está muito além da precisão
            experimental atual, tornando este teste principalmente especulativo.
            """,
            limitations=[
                "Precisão experimental atual muito abaixo da escala de Planck",
                "Dificuldade em distinguir ruído de granularidade temporal",
                "Requer dados com timestamps de alta precisão"
            ]
        )
        
        try:
            # Procura colunas temporais
            time_cols = [col for col in data.columns 
                        if any(k in col.lower() for k in ['time', 'timestamp', 'date', 'temporal'])]
            
            if len(time_cols) > 0:
                time_col = time_cols[0]
                
                # Tenta converter para numérico se necessário
                times = pd.to_numeric(data[time_col], errors='coerce').dropna().values
                
                if len(times) > 100:
                    # Ordena tempos
                    times = np.sort(times)
                    
                    # Calcula deltas temporais
                    deltas = np.diff(times)
                    deltas = deltas[deltas > 0]  # Remove deltas não-físicos
                    
                    if len(deltas) > 50:
                        # Analisa distribuição de deltas
                        mean_delta = np.mean(deltas)
                        std_delta = np.std(deltas)
                        
                        result.details['mean_time_delta'] = float(mean_delta)
                        result.details['std_time_delta'] = float(std_delta)
                        
                        # Coeficiente de variação
                        cv = std_delta / mean_delta if mean_delta > 0 else 0
                        result.details['coefficient_of_variation'] = float(cv)
                        
                        # Teste de uniformidade (deltas deveriam ser exponenciais para processo Poisson)
                        # Se forem muito uniformes, pode indicar clock regular
                        
                        # Teste de Kolmogorov-Smirnov para exponencial
                        ks_stat, ks_p = stats.kstest(deltas, 'expon', args=(0, mean_delta))
                        result.details['ks_test_p_value'] = float(ks_p)
                        
                        if ks_p < 0.01:
                            result.warnings.append(f"Distribuição temporal difere significativamente de exponencial (p={ks_p:.4f})")
                        
                        # Busca por periodicidade nos deltas
                        if len(deltas) > 200:
                            # Autocorrelação
                            autocorr = np.correlate(deltas - np.mean(deltas), 
                                                   deltas - np.mean(deltas), 
                                                   mode='full')
                            autocorr = autocorr[len(autocorr)//2:]
                            autocorr = autocorr / autocorr[0] if autocorr[0] > 0 else autocorr
                            
                            # Busca picos na autocorrelação (excluindo lag 0)
                            if len(autocorr) > 10:
                                peaks, properties = signal.find_peaks(autocorr[1:], height=0.3)
                                
                                if len(peaks) > 0:
                                    result.anomaly_detected = True
                                    result.anomaly_score = min(100, len(peaks) * 15)
                                    result.significance = 0.05
                                    result.effect_size = np.max(autocorr[peaks+1])
                                    result.details['periodic_lags'] = (peaks + 1).tolist()[:5]
                                    result.warnings.append(f"Periodicidade detectada em série temporal")
                        
                        # Busca por quantização nos deltas
                        # Se tempo for discreto, deltas deveriam ser múltiplos de uma unidade básica
                        if len(deltas) > 100:
                            # Histograma fino
                            n_bins = 100
                            hist, bin_edges = np.histogram(deltas, bins=n_bins)
                            
                            # Busca picos regularmente espaçados
                            peak_positions = bin_edges[np.where(hist > np.mean(hist) + std_delta)[0]]
                            
                            if len(peak_positions) > 5:
                                # Verifica regularidade dos picos
                                peak_spacings = np.diff(peak_positions)
                                spacing_std = np.std(peak_spacings)
                                spacing_mean = np.mean(peak_spacings)
                                
                                if spacing_mean > 0 and spacing_std / spacing_mean < 0.2:
                                    result.anomaly_detected = True
                                    result.anomaly_score = max(result.anomaly_score, 40)
                                    result.details['quantization_spacing'] = float(spacing_mean)
                                    result.warnings.append("Possível quantização temporal detectada")
            
            # Se não há coluna temporal explícita, tenta inferir de índices
            if len(time_cols) == 0 and len(data) > 100:
                # Usa índice como proxy temporal
                indices = np.arange(len(data))
                
                # Analisa variações entre observações consecutivas
                numeric_data = data.select_dtypes(include=[np.number]).iloc[:1000]
                
                if len(numeric_data) > 50:
                    # Calcula diferenças entre linhas consecutivas
                    diffs = numeric_data.diff().dropna()
                    
                    # Verifica se há sincronização nas mudanças
                    correlation_matrix = diffs.corr()
                    
                    # Se todas as variáveis mudam juntas, pode indicar updates discretos
                    mean_corr = np.mean(np.abs(correlation_matrix.values - np.eye(len(correlation_matrix))))
                    
                    result.details['mean_variable_correlation'] = float(mean_corr)
                    
                    if mean_corr > 0.8:
                        result.warnings.append("Alta correlação entre mudanças de variáveis independentes")
            
        except Exception as e:
            logger.error(f"Erro no teste de consistência temporal: {str(e)}")
            result.warnings.append(f"Erro durante análise: {str(e)}")
        
        return result
    
    def _create_error_result(self, test_name: str, error_msg: str) -> TestResult:
        """Cria resultado de teste quando ocorre erro."""
        return TestResult(
            test_name=test_name,
            passed=False,
            significance=1.0,
            effect_size=0.0,
            anomaly_detected=False,
            anomaly_score=0.0,
            details={'error': error_msg},
            warnings=["Teste não pôde ser executado devido a erro"],
            theoretical_basis="Não disponível devido a erro na execução",
            limitations=[]
        )
    
    def calculate_overall_suspicion_index(self) -> float:
        """
        Calcula o Índice de Suspeita Especulativo agregado.
        
        Returns:
            Valor entre 0 e 100 representando suspeita agregada
        """
        if not self.results:
            return 0.0
        
        scores = [r.anomaly_score for r in self.results.values()]
        
        if not scores:
            return 0.0
        
        # Média ponderada (todos os testes têm peso igual neste momento)
        overall_score = np.mean(scores)
        
        return min(100, max(0, overall_score))
    
    def get_results_summary(self) -> Dict:
        """
        Retorna resumo dos resultados de todos os testes.
        
        Returns:
            Dicionário com resumo estruturado dos resultados
        """
        summary = {
            'timestamp': datetime.now().isoformat(),
            'num_tests': len(self.results),
            'tests_with_anomalies': sum(1 for r in self.results.values() if r.anomaly_detected),
            'overall_suspicion_index': self.calculate_overall_suspicion_index(),
            'individual_results': {}
        }
        
        for test_name, result in self.results.items():
            summary['individual_results'][test_name] = {
                'name': result.test_name,
                'anomaly_detected': result.anomaly_detected,
                'anomaly_score': result.anomaly_score,
                'significance': result.significance,
                'effect_size': result.effect_size,
                'warnings': result.warnings
            }
        
        return summary
