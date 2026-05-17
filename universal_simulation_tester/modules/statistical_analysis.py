"""
Módulo de Análise Estatística

Fornece ferramentas estatísticas avançadas para:
- Calcular significância estatística
- Implementar correções para múltiplas comparações
- Gerar distribuições nulas via Monte Carlo
- Calcular fatores de Bayes
- Fornecer intervalos de confiança
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StatisticalResult:
    """Resultado de análise estatística."""
    statistic: float
    p_value: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    power: float
    bayes_factor: Optional[float] = None


class StatisticalAnalysis:
    """
    Classe para análises estatísticas avançadas.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.significance_level = self.config.get('significance_level', 0.05)
        self.confidence_level = self.config.get('confidence_level', 0.95)
        self.monte_carlo_iterations = self.config.get('monte_carlo_iterations', 10000)
    
    def calculate_significance(self, 
                               observed: np.ndarray, 
                               expected: float,
                               test_type: str = 't') -> StatisticalResult:
        """
        Calcula significância estatística de uma observação.
        
        Args:
            observed: Dados observados
            expected: Valor esperado sob hipótese nula
            test_type: Tipo de teste ('t', 'z', 'chi2')
            
        Returns:
            StatisticalResult com métricas estatísticas
        """
        n = len(observed)
        mean_obs = np.mean(observed)
        std_obs = np.std(observed, ddof=1)
        
        # Teste t
        if test_type == 't':
            t_stat = (mean_obs - expected) / (std_obs / np.sqrt(n))
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=n-1))
        
        # Intervalo de confiança
        alpha = 1 - self.confidence_level
        ci = stats.t.interval(self.confidence_level, df=n-1, 
                             loc=mean_obs, scale=std_obs/np.sqrt(n))
        
        # Effect size (Cohen's d)
        effect_size = (mean_obs - expected) / std_obs if std_obs > 0 else 0
        
        # Power analysis
        power = self._calculate_power(effect_size, n, alpha)
        
        return StatisticalResult(
            statistic=t_stat if test_type == 't' else 0,
            p_value=p_value,
            confidence_interval=ci,
            effect_size=effect_size,
            power=power
        )
    
    def bonferroni_correction(self, p_values: List[float]) -> List[float]:
        """
        Aplica correção de Bonferroni para múltiplas comparações.
        
        Args:
            p_values: Lista de valores-p
            
        Returns:
            Lista de valores-p corrigidos
        """
        n = len(p_values)
        corrected = [min(1, p * n) for p in p_values]
        logger.info(f"Correção de Bonferroni aplicada: {n} testes")
        return corrected
    
    def fdr_correction(self, p_values: List[float]) -> List[float]:
        """
        Aplica correção False Discovery Rate (Benjamini-Hochberg).
        
        Args:
            p_values: Lista de valores-p
            
        Returns:
            Lista de valores-p corrigidos
        """
        n = len(p_values)
        sorted_indices = np.argsort(p_values)
        sorted_p = np.array(p_values)[sorted_indices]
        
        # Benjamini-Hochberg
        ranks = np.arange(1, n + 1)
        corrected = sorted_p * n / ranks
        
        # Garante monotonicidade
        for i in range(n - 2, -1, -1):
            corrected[i] = min(corrected[i], corrected[i + 1])
        
        corrected = np.minimum(corrected, 1.0)
        
        # Retorna na ordem original
        result = np.zeros(n)
        result[sorted_indices] = corrected
        
        logger.info(f"Correção FDR aplicada: {n} testes")
        return result.tolist()
    
    def monte_carlo_null_distribution(self, 
                                      statistic_func,
                                      data: np.ndarray,
                                      n_iterations: int = None) -> np.ndarray:
        """
        Gera distribuição nula via método de Monte Carlo.
        
        Args:
            statistic_func: Função que calcula a estatística de interesse
            data: Dados observados
            n_iterations: Número de iterações
            
        Returns:
            Array com valores da estatística sob hipótese nula
        """
        n_iter = n_iterations or self.monte_carlo_iterations
        n = len(data)
        
        null_stats = np.zeros(n_iter)
        
        for i in range(n_iter):
            # Reamostra sob hipótese nula (permutação)
            shuffled = np.random.permutation(data)
            null_stats[i] = statistic_func(shuffled)
        
        logger.info(f"Distribuição nula gerada: {n_iter} iterações")
        return null_stats
    
    def calculate_bayes_factor(self, 
                               data: np.ndarray,
                               null_mean: float,
                               null_std: float,
                               alternative_std: float = None) -> float:
        """
        Calcula fator de Bayes para comparação de modelos.
        
        Args:
            data: Dados observados
            null_mean: Média sob hipótese nula
            null_std: Desvio padrão sob hipótese nula
            alternative_std: Desvio padrão sob alternativa
            
        Returns:
            Fator de Bayes (BF > 1 favorece alternativa)
        """
        n = len(data)
        mean_data = np.mean(data)
        
        # Verossimilhança sob H0
        likelihood_h0 = np.prod(stats.norm.pdf(data, loc=null_mean, scale=null_std))
        
        # Verossimilhança sob H1 (usando média observada como estimativa)
        alt_mean = mean_data
        alt_std = alternative_std or np.std(data, ddof=1)
        likelihood_h1 = np.prod(stats.norm.pdf(data, loc=alt_mean, scale=alt_std))
        
        if likelihood_h0 > 0:
            bf = likelihood_h1 / likelihood_h0
        else:
            bf = float('inf')
        
        logger.info(f"Fator de Bayes calculado: BF={bf:.4f}")
        return bf
    
    def _calculate_power(self, effect_size: float, n: int, alpha: float) -> float:
        """Calcula poder estatístico do teste."""
        # Aproximação para teste t
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = effect_size * np.sqrt(n) - z_alpha
        power = stats.norm.cdf(z_beta)
        return max(0, min(1, power))
    
    def detect_outliers_sigma(self, 
                              data: np.ndarray, 
                              n_sigma: float = 3.0) -> np.ndarray:
        """
        Detecta outliers baseados em desvios padrão.
        
        Args:
            data: Dados
            n_sigma: Número de desvios padrão para limiar
            
        Returns:
            Máscara booleana indicando outliers
        """
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        if std == 0:
            return np.zeros(len(data), dtype=bool)
        
        outliers = np.abs(data - mean) > n_sigma * std
        logger.info(f"Detectados {sum(outliers)} outliers ({n_sigma} sigma)")
        return outliers
    
    def bootstrap_confidence_interval(self,
                                      data: np.ndarray,
                                      statistic_func,
                                      n_bootstrap: int = 1000,
                                      confidence_level: float = None) -> Tuple[float, float]:
        """
        Calcula intervalo de confiança via bootstrap.
        
        Args:
            data: Dados observados
            statistic_func: Função que calcula a estatística
            n_bootstrap: Número de amostras bootstrap
            confidence_level: Nível de confiança
            
        Returns:
            Tupla com limite inferior e superior
        """
        conf = confidence_level or self.confidence_level
        n = len(data)
        
        bootstrap_stats = np.zeros(n_bootstrap)
        
        for i in range(n_bootstrap):
            # Amostra com reposição
            indices = np.random.choice(n, size=n, replace=True)
            sample = data[indices]
            bootstrap_stats[i] = statistic_func(sample)
        
        # Intervalo percentil
        alpha = 1 - conf
        lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
        upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))
        
        logger.info(f"Bootstrap CI calculado: [{lower:.4f}, {upper:.4f}]")
        return (lower, upper)
    
    def warn_about_phacking(self, num_tests: int) -> str:
        """
        Gera aviso sobre p-hacking e viés de seleção.
        
        Args:
            num_tests: Número de testes realizados
            
        Returns:
            String com aviso educativo
        """
        warning = f"""
        ⚠️ ALERTA SOBRE P-HACKING E VIÉS DE SELEÇÃO ⚠️
        
        Você realizou {num_tests} testes estatísticos. Mesmo que todos os 
        fenômenos sejam puramente aleatórios, espera-se encontrar aproximadamente
        {num_tests * self.significance_level:.1f} resultados "significativos" 
        por acaso (ao nível α={self.significance_level}).
        
        Recomendações:
        1. Aplique correções para múltiplas comparações (Bonferroni ou FDR)
        2. Não selecione apenas resultados significativos para reportar
        3. Considere o tamanho do efeito, não apenas o valor-p
        4. Replicação independente é essencial
        5. Lembre-se: correlação não implica causalidade
        
        Em ciência, resultados negativos (ausência de anomalias) são tão 
        importantes quanto resultados positivos!
        """
        return warning
