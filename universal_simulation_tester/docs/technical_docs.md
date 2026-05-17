# Documentação Técnica - Universal Simulation Hypothesis Tester

## Índice

1. [Introdução](#introdução)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Módulos Principais](#módulos-principais)
4. [Testes Científicos Implementados](#testes-científicos-implementados)
5. [API Reference](#api-reference)
6. [Exemplos de Uso](#exemplos-de-uso)

---

## Introdução

Este documento descreve a arquitetura técnica e implementação dos testes científicos para investigação da hipótese de simulação universal.

### Objetivo Científico

Investigar padrões estatísticos anômalos que poderiam ser consistentes com limitações esperadas em um universo simulado, sempre mantendo o ceticismo científico adequado.

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Streamlit                       │
│                         (app.py)                             │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  DataLoader   │   │SimulationTests  │   │StatisticalAnalysis│
└───────────────┘   └─────────────────┘   └─────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│Visualization  │   │ReportGenerator  │   │EducationalContent│
└───────────────┘   └─────────────────┘   └─────────────────┘
```

---

## Módulos Principais

### 1. DataLoader (`modules/data_loader.py`)

**Responsabilidades:**
- Carregar dados CSV, JSON, FITS
- Gerar dados simulados (CMB, partículas quânticas, raios cósmicos)
- Validar e pré-processar dados

**Classes Principais:**
```python
class DataLoader:
    def load_csv(filepath: str) -> pd.DataFrame
    def load_json(filepath: str) -> pd.DataFrame
    def generate_simulated_data(data_type: str, num_samples: int, seed: int) -> pd.DataFrame
```

### 2. SimulationTests (`modules/simulation_tests.py`)

**Responsabilidades:**
- Implementar 6 testes científicos especulativos
- Calcular scores de anomalia (0-100)
- Detectar padrões suspeitos

**Testes Implementados:**
1. `test_spacetime_discretization()` - Busca estrutura granular
2. `test_rounding_errors()` - Analisa constantes em bases numéricas
3. `test_nonlocal_correlations()` - Testes de Bell
4. `test_isotropy_homogeneity()` - Análise de CMB
5. `test_resource_limitations()` - Procura "LOD" dinâmico
6. `test_temporal_consistency()` - Investiga tempo discreto

### 3. StatisticalAnalysis (`modules/statistical_analysis.py`)

**Responsabilidades:**
- Calcular p-values e significância
- Correções Bonferroni e FDR
- Métodos de Monte Carlo
- Fatores de Bayes

---

## Testes Científicos Implementados

### Teste 1: Discretização do Espaço-Tempo

**Base Teórica:** Se o universo é simulado, pode ter resolução finita (escala de Planck: ~1.6×10⁻³⁵ m).

**Metodologia:**
1. Aplicar transformada de Fourier nos dados espaciais
2. Buscar picos de frequência suspeitos
3. Calcular resíduos entre modelo contínuo e observado
4. Estimar limite superior para "tamanho do pixel"

**Evidência Positiva:**
- Padrões periódicos em análise de Fourier
- Desvios sistemáticos de previsões contínuas
- Direções privilegiadas no espaço

### Teste 2: Erros de Arredondamento Cósmico

**Base Teórica:** Computadores usam precisão finita (float32/float64), podendo causar truncamentos.

**Metodologia:**
1. Analisar constantes fundamentais (α, G, c, h)
2. Converter para múltiplas bases (binária, decimal, hexadecimal)
3. Buscar padrões de repetição ou terminações suspeitas
4. Comparar com simulações de diferentes precisões

**Evidência Positiva:**
- Terminações abruptas em representação binária
- Rationalidade suspeita entre constantes
- Padrões repetitivos em alta precisão

### Teste 3: Correlações Não-Locais Anômalas

**Base Teórica:** Emaranhamento quântico tem limite teórico (Tsirelson: 2√2 ≈ 2.828).

**Metodologia:**
1. Simular teste CHSH/Bell com N partículas
2. Calcular parâmetro S
3. Verificar violações do limite de Tsirelson
4. Buscar padrões periódicos nas correlações

**Evidência Positiva:**
- Violação do limite de Tsirelson
- Estruturas tipo código de correção de erro
- Otimizações computacionais suspeitas

### Teste 4: Isotropia e Homogeneidade

**Base Teórica:** Universo deveria ser isotrópico. Simulação poderia ter eixos de coordenadas privilegiados.

**Metodologia:**
1. Analisar mapa de temperatura do CMB
2. Calcular multipolos esféricos
3. Buscar alinhamentos anômalos ("Axis of Evil")
4. Detectar assimetrias hemisféricas

**Evidência Positiva:**
- Eixos de alinhamento multipolar
- Assimetrias Norte-Sul sistemáticas
- Padrões que sugerem grid computacional

### Teste 5: Limitação de Recursos

**Base Teórica:** Simulações otimizam recursos (Level of Detail, renderização sob demanda).

**Metodologia:**
1. Analisar distribuição de energias de raios cósmicos
2. Buscar corte em altas energias (limite GZK)
3. Verificar se fenômenos quânticos dependem de observação
4. Detectar "lazy evaluation" em processos físicos

**Evidência Positiva:**
- Corte abrupto em espectro de energia
- Complexidade máxima em sistemas físicos
- Dependência de observação não prevista

### Teste 6: Consistência Temporal

**Base Teórica:** Tempo pode ser discreto (tempo de Planck: ~5.4×10⁻⁴⁴ s).

**Metodologia:**
1. Analisar flutuações quânticas temporais
2. Buscar periodicidade em eventos
3. Verificar sincronização suspeita
4. Testar granularidade temporal

**Evidência Positiva:**
- "Frames" temporais discretos
- Clock global detectável
- Padrões temporais em flutuações

---

## API Reference

### SimulationTests

```python
from modules.simulation_tests import SimulationTests

tests = SimulationTests(config={})

# Executar todos os testes
results = tests.run_all_tests(data)

# Executar teste individual
result = tests.test_spacetime_discretization(data)

# Calcular índice agregado
score = tests.calculate_overall_suspicion_index()
```

### StatisticalAnalysis

```python
from modules.statistical_analysis import StatisticalAnalysis

stats = StatisticalAnalysis(config={'significance_level': 0.05})

# Teste de significância
result = stats.calculate_significance(observed, expected)

# Correção para múltiplas comparações
corrected = stats.bonferroni_correction(p_values, n_tests)

# Fator de Bayes
bf = stats.calculate_bayes_factor(model1, model2, data)
```

---

## Exemplos de Uso

### Exemplo 1: Análise Completa

```python
from modules.data_loader import DataLoader
from modules.simulation_tests import SimulationTests

# Carregar dados
dl = DataLoader()
data = dl.generate_simulated_data('cosmic_microwave', 10000, seed=42)

# Executar testes
st = SimulationTests()
results = st.run_all_tests(data)

# Ver resultados
for test_name, result in results.items():
    print(f"{test_name}: {result.anomaly_score:.1f}/100 (p={result.significance:.4f})")

# Índice agregado
score = st.calculate_overall_suspicion_index()
print(f"Índice de Suspeita: {score:.1f}%")
```

### Exemplo 2: Exportar Relatório

```python
from modules.report_generator import ReportGenerator

rg = ReportGenerator()

# Exportar JSON
rg.export_to_json(results, 'resultados.json')

# Gerar LaTeX
latex = rg.generate_latex(results, score)
with open('artigo.tex', 'w') as f:
    f.write(latex)
```

---

## Considerações Finais

Este software é uma ferramenta **educacional e exploratória**. Os resultados são:
- **Especulativos**: Não constituem evidência científica
- **Não-conclusivos**: Anomalias têm explicações alternativas
- **Experimentais**: Metodologia em desenvolvimento

Sempre consulte físicos profissionais e literatura revisada por pares antes de divulgar conclusões.

---

**Versão:** 1.0.0  
**Última atualização:** 2024  
**Licença:** MIT (educacional)
