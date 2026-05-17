"""
Módulo de Carregamento e Processamento de Dados

Responsável por:
- Carregar dados de arquivos CSV, JSON e FITS
- Gerar dados simulados para demonstração
- Conectar-se a APIs públicas de dados astronômicos
- Pré-processar e validar dados de entrada
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Classe para carregamento e processamento de dados cosmológicos.
    
    Suporta múltiplos formatos de entrada e fornece dados simulados
    para fins de demonstração e teste.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o DataLoader com configuração opcional.
        
        Args:
            config: Dicionário de configuração com parâmetros opcionais
        """
        self.config = config or {}
        self.data = None
        self.metadata = {}
        logger.info("DataLoader inicializado")
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Carrega dados de um arquivo CSV.
        
        Args:
            filepath: Caminho para o arquivo CSV
            
        Returns:
            DataFrame com os dados carregados
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se o formato for inválido
        """
        logger.info(f"Carregando CSV: {filepath}")
        try:
            self.data = pd.read_csv(filepath)
            self.metadata['source'] = filepath
            self.metadata['format'] = 'csv'
            self.metadata['loaded_at'] = datetime.now().isoformat()
            self.metadata['num_rows'] = len(self.data)
            self.metadata['num_cols'] = len(self.data.columns)
            logger.info(f"CSV carregado com sucesso: {self.metadata['num_rows']} linhas, {self.metadata['num_cols']} colunas")
            return self.data
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {str(e)}")
            raise
    
    def load_json(self, filepath: str) -> pd.DataFrame:
        """
        Carrega dados de um arquivo JSON.
        
        Args:
            filepath: Caminho para o arquivo JSON
            
        Returns:
            DataFrame com os dados carregados
        """
        logger.info(f"Carregando JSON: {filepath}")
        try:
            with open(filepath, 'r') as f:
                json_data = json.load(f)
            
            # Normaliza JSON aninhado
            self.data = pd.json_normalize(json_data)
            self.metadata['source'] = filepath
            self.metadata['format'] = 'json'
            self.metadata['loaded_at'] = datetime.now().isoformat()
            self.metadata['num_rows'] = len(self.data)
            self.metadata['num_cols'] = len(self.data.columns)
            logger.info(f"JSON carregado com sucesso")
            return self.data
        except Exception as e:
            logger.error(f"Erro ao carregar JSON: {str(e)}")
            raise
    
    def load_fits(self, filepath: str) -> pd.DataFrame:
        """
        Carrega dados de um arquivo FITS (formato astronômico).
        
        Args:
            filepath: Caminho para o arquivo FITS
            
        Returns:
            DataFrame com os dados carregados
        """
        logger.info(f"Carregando FITS: {filepath}")
        try:
            from astropy.io import fits
            
            with fits.open(filepath) as hdul:
                # Tenta carregar a primeira extensão com dados tabulares
                for hdu in hdul:
                    if hasattr(hdu, 'data') and hdu.data is not None:
                        self.data = pd.DataFrame(hdu.data)
                        break
                
                self.metadata['source'] = filepath
                self.metadata['format'] = 'fits'
                self.metadata['loaded_at'] = datetime.now().isoformat()
                self.metadata['num_rows'] = len(self.data)
                self.metadata['num_cols'] = len(self.data.columns)
                logger.info(f"FITS carregado com sucesso")
                return self.data
        except ImportError:
            logger.warning("astropy não instalado. Não é possível carregar FITS.")
            raise ImportError("Instale astropy para carregar arquivos FITS: pip install astropy")
        except Exception as e:
            logger.error(f"Erro ao carregar FITS: {str(e)}")
            raise
    
    def generate_simulated_data(self, 
                                data_type: str = 'cosmic_microwave',
                                num_samples: int = 10000,
                                seed: Optional[int] = None) -> pd.DataFrame:
        """
        Gera dados simulados para demonstração e teste.
        
        Args:
            data_type: Tipo de dado simulado
                - 'cosmic_microwave': Radiação cósmica de fundo simulada
                - 'quantum_particles': Partículas quânticas simuladas
                - 'cosmic_rays': Raios cósmicos simulados
                - 'constants': Constantes físicas com ruído
            num_samples: Número de amostras a gerar
            seed: Seed para reprodutibilidade
            
        Returns:
            DataFrame com dados simulados
        """
        if seed is not None:
            np.random.seed(seed)
        
        logger.info(f"Gerando dados simulados: {data_type} com {num_samples} amostras")
        
        if data_type == 'cosmic_microwave':
            self.data = self._simulate_cmb_data(num_samples)
        elif data_type == 'quantum_particles':
            self.data = self._simulate_quantum_data(num_samples)
        elif data_type == 'cosmic_rays':
            self.data = self._simulate_cosmic_rays(num_samples)
        elif data_type == 'constants':
            self.data = self._simulate_constants(num_samples)
        else:
            raise ValueError(f"Tipo de dado desconhecido: {data_type}")
        
        self.metadata['source'] = 'simulated'
        self.metadata['data_type'] = data_type
        self.metadata['num_samples'] = num_samples
        self.metadata['generated_at'] = datetime.now().isoformat()
        
        logger.info(f"Dados simulados gerados com sucesso")
        return self.data
    
    def _simulate_cmb_data(self, num_samples: int) -> pd.DataFrame:
        """
        Simula dados de radiação cósmica de fundo.
        
        Args:
            num_samples: Número de amostras
            
        Returns:
            DataFrame com dados CMB simulados
        """
        # Coordenadas angulares no céu
        theta = np.random.uniform(0, np.pi, num_samples)
        phi = np.random.uniform(0, 2*np.pi, num_samples)
        
        # Temperatura base (2.725 K) com flutuações gaussianas
        T_base = 2.725
        delta_T = np.random.normal(0, 1e-5, num_samples)
        temperature = T_base + delta_T
        
        # Adiciona algumas anomalias sutis (para teste)
        anomaly_mask = np.random.random(num_samples) < 0.01
        temperature[anomaly_mask] += np.random.normal(0, 5e-5, sum(anomaly_mask))
        
        data = pd.DataFrame({
            'theta': theta,
            'phi': phi,
            'temperature_K': temperature,
            'delta_T_T': delta_T / T_base
        })
        
        return data
    
    def _simulate_quantum_data(self, num_samples: int) -> pd.DataFrame:
        """
        Simula dados de partículas quânticas para testes de Bell.
        
        Args:
            num_samples: Número de medições
            
        Returns:
            DataFrame com dados quânticos simulados
        """
        # Ângulos de medição
        angle_a = np.random.uniform(0, 2*np.pi, num_samples)
        angle_b = np.random.uniform(0, 2*np.pi, num_samples)
        
        # Resultados das medições (+1 ou -1)
        # Simula correlações quânticas com violação de Bell
        diff_angle = angle_a - angle_b
        correlation = -np.cos(diff_angle)
        
        # Gera resultados correlacionados
        result_a = np.random.choice([-1, 1], num_samples)
        prob_same = (1 + correlation) / 2
        result_b = np.where(np.random.random(num_samples) < prob_same, result_a, -result_a)
        
        data = pd.DataFrame({
            'angle_a_rad': angle_a,
            'angle_b_rad': angle_b,
            'result_a': result_a,
            'result_b': result_b,
            'correlation_expected': correlation
        })
        
        return data
    
    def _simulate_cosmic_rays(self, num_samples: int) -> pd.DataFrame:
        """
        Simula dados de raios cósmicos de ultra-alta energia.
        
        Args:
            num_samples: Número de eventos
            
        Returns:
            DataFrame com dados de raios cósmicos
        """
        # Energias seguem lei de potência (GZK cutoff)
        energies = np.random.power(2.7, num_samples) * 1e20  # eV
        
        # Direções de chegada
        ra = np.random.uniform(0, 360, num_samples)  # Ascensão reta
        dec = np.random.uniform(-90, 90, num_samples)  # Declinação
        
        # Tempo de chegada
        timestamps = np.sort(np.random.uniform(0, 365*10, num_samples))  # dias
        
        data = pd.DataFrame({
            'energy_eV': energies,
            'right_ascension_deg': ra,
            'declination_deg': dec,
            'timestamp_days': timestamps
        })
        
        return data
    
    def _simulate_constants(self, num_samples: int) -> pd.DataFrame:
        """
        Simula medições de constantes físicas fundamentais.
        
        Args:
            num_samples: Número de medições simuladas
            
        Returns:
            DataFrame com constantes físicas
        """
        # Valores aceitos das constantes (CODATA 2018)
        constants = {
            'fine_structure': 7.2973525693e-3,  # alpha
            'proton_electron_ratio': 1836.15267343,  # mp/me
            'gravitational': 6.67430e-11,  # G (m^3 kg^-1 s^-2)
            'planck': 6.62607015e-34,  # h (J s)
            'speed_of_light': 299792458,  # c (m/s)
            'boltzmann': 1.380649e-23,  # k_B (J/K)
        }
        
        data_dict = {}
        for name, value in constants.items():
            # Adiciona ruído gaussiano pequeno (incerteza experimental)
            noise_std = abs(value) * 1e-10
            measurements = value + np.random.normal(0, noise_std, num_samples)
            data_dict[name] = measurements
        
        data_dict['measurement_id'] = range(num_samples)
        
        return pd.DataFrame(data_dict)
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        """
        Valida os dados carregados.
        
        Returns:
            Tupla (é_válido, lista_de_erros)
        """
        errors = []
        
        if self.data is None:
            errors.append("Nenhum dado carregado")
            return False, errors
        
        # Verifica valores nulos
        null_counts = self.data.isnull().sum()
        if null_counts.any():
            cols_with_nulls = null_counts[null_counts > 0].index.tolist()
            errors.append(f"Valores nulos nas colunas: {cols_with_nulls}")
        
        # Verifica se há dados
        if len(self.data) == 0:
            errors.append("DataFrame vazio")
        
        # Verifica tipos de dados
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                try:
                    pd.to_numeric(self.data[col])
                except (ValueError, TypeError):
                    errors.append(f"Coluna '{col}' contém dados não-numéricos")
        
        is_valid = len(errors) == 0
        logger.info(f"Validação: {'OK' if is_valid else 'FALHOU'} - {len(errors)} erros")
        return is_valid, errors
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Retorna os dados carregados."""
        return self.data
    
    def get_metadata(self) -> Dict:
        """Retorna metadados dos dados."""
        return self.metadata
    
    def preprocess_data(self, 
                       normalize: bool = True,
                       remove_outliers: bool = False,
                       outlier_sigma: float = 3.0) -> pd.DataFrame:
        """
        Pré-processa os dados carregados.
        
        Args:
            normalize: Se True, normaliza os dados para média 0 e variância 1
            remove_outliers: Se True, remove outliers além de outlier_sigma desvios padrão
            outlier_sigma: Número de desvios padrão para definir outliers
            
        Returns:
            DataFrame pré-processado
        """
        if self.data is None:
            raise ValueError("Nenhum dado carregado")
        
        processed = self.data.copy()
        
        # Seleciona apenas colunas numéricas
        numeric_cols = processed.select_dtypes(include=[np.number]).columns
        
        if normalize:
            # Normalização z-score
            for col in numeric_cols:
                mean = processed[col].mean()
                std = processed[col].std()
                if std > 0:
                    processed[f'{col}_normalized'] = (processed[col] - mean) / std
        
        if remove_outliers:
            # Remove outliers
            mask = np.ones(len(processed), dtype=bool)
            for col in numeric_cols:
                mean = processed[col].mean()
                std = processed[col].std()
                if std > 0:
                    col_mask = np.abs(processed[col] - mean) <= outlier_sigma * std
                    mask &= col_mask
            processed = processed[mask]
            logger.info(f"Removidos {len(self.data) - len(processed)} outliers")
        
        return processed
    
    def save_processed_data(self, filepath: str, format: str = 'csv') -> None:
        """
        Salva os dados processados em arquivo.
        
        Args:
            filepath: Caminho do arquivo de saída
            format: Formato do arquivo ('csv', 'json', 'hdf5')
        """
        if self.data is None:
            raise ValueError("Nenhum dado para salvar")
        
        logger.info(f"Salvando dados em {filepath}")
        
        if format == 'csv':
            self.data.to_csv(filepath, index=False)
        elif format == 'json':
            self.data.to_json(filepath, orient='records', indent=2)
        elif format == 'hdf5':
            self.data.to_hdf(filepath, key='data', mode='w')
        else:
            raise ValueError(f"Formato não suportado: {format}")
        
        logger.info(f"Dados salvos com sucesso")
