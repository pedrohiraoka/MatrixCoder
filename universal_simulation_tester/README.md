# Universal Simulation Hypothesis Tester

## Visão Geral

Este aplicativo é uma ferramenta educacional e exploratória que implementa uma bateria de testes científicos especulativos para investigar padrões que poderiam sugerir que nosso universo é uma simulação computacional.

## ⚠️ AVISO IMPORTANTE

**ESTE APLICATIVO É UMA FERRAMENTA EDUCACIONAL E EXPLORATÓRIA.** A hipótese de que vivemos em uma simulação é uma questão filosófica fascinante, mas atualmente não existe método científico estabelecido que possa prová-la ou refutá-la definitivamente.

## Instalação

### Pré-requisitos
- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. Clone o repositório ou navegue até a pasta do projeto:
```bash
cd universal_simulation_tester
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
streamlit run app.py
```

## Estrutura do Projeto

```
universal_simulation_tester/
├── app.py                  # Aplicação principal Streamlit
├── config.yaml            # Arquivo de configuração
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── modules/              # Módulos principais
│   ├── __init__.py
│   ├── data_loader.py    # Carregamento e processamento de dados
│   ├── simulation_tests.py # Motor de testes científicos
│   ├── statistical_analysis.py # Análise estatística
│   ├── visualization.py  # Visualizações e gráficos
│   ├── report_generator.py # Geração de relatórios
│   └── educational.py    # Conteúdo educacional
├── data/                 # Conjuntos de dados
│   ├── sample_data.csv   # Dados de exemplo
│   └── ...
├── docs/                 # Documentação
├── exports/              # Relatórios e exportações
├── tests/                # Testes unitários
└── assets/               # Recursos visuais
```

## Funcionalidades Principais

### 1. Módulo de Entrada de Dados
- Upload de arquivos CSV, JSON e FITS
- Dados simulados para demonstração
- Parâmetros configuráveis de simulação
- Conexão com APIs astronômicas públicas

### 2. Motor de Testes Científicos
Seis testes especulativos implementados:

1. **Teste de Discretização do Espaço-Tempo**: Busca evidências de estrutura granular
2. **Teste de Erros de Arredondamento Cósmico**: Analisa constantes fundamentais
3. **Teste de Correlações Não-Locais Anômalas**: Simula testes de Bell
4. **Teste de Isotropia e Homogeneidade**: Analisa radiação cósmica de fundo
5. **Teste de Limitação de Recursos**: Busca "Level of Detail" dinâmico
6. **Teste de Consistência Temporal**: Investiga granularidade temporal

### 3. Análise Estatística
- Significância estatística com correções para múltiplas comparações
- Métodos de Monte Carlo para distribuições nulas
- Fatores de Bayes e intervalos de confiança
- Alertas sobre p-hacking e viés de seleção

### 4. Dashboard Interativo
- Índice de Suspeita Especulativa (0-100%)
- Gráfico radar comparando todos os testes
- Visualizações detalhadas interativas
- Relatório final com ressalvas científicas

### 5. Módulo Educacional
- Explicações acessíveis sobre cada teste
- Biografias de físicos relevantes
- Seção "Mitos e Verdades"
- Glossário de termos técnicos

### 6. Exportação
- Relatórios em PDF
- Apresentações PowerPoint
- Dados em CSV, JSON, HDF5
- Código LaTeX para artigos científicos

## Uso Básico

1. **Inicialização**: Ao abrir o aplicativo, leia o aviso legal completo
2. **Carregar Dados**: Use dados de exemplo ou faça upload dos seus próprios dados
3. **Configurar Parâmetros**: Ajuste os parâmetros de simulação conforme necessário
4. **Executar Testes**: Clique em "Executar Bateria de Testes"
5. **Analisar Resultados**: Explore o dashboard e visualizações
6. **Exportar**: Gere relatórios e compartilhe resultados

## Configuração

O arquivo `config.yaml` permite personalizar:
- Número de partículas para testes quânticos
- Faixa de energia para análise de raios cósmicos
- Resolução para análise de discretização
- Bases numéricas para testes de padrões
- Tempo máximo de processamento

## Limitações e Ressalvas

- Os resultados são **especulativos** e **não-conclusivos**
- Anomalias estatísticas podem ter explicações naturais
- O aplicativo testa hipóteses específicas, não prova a hipótese geral
- Ausência de anomalias também não refuta a hipótese de simulação
- Consulte físicos profissionais antes de divulgar conclusões

## Contribuição

Contribuições são bem-vindas! Por favor:
1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Adicione testes unitários
4. Submeta um pull request

## Referências Científicas

- Bostrom, N. (2003). "Are You Living in a Computer Simulation?"
- Tegmark, M. (2007). "The Mathematical Universe"
- Planck Collaboration (2018). "Planck 2018 results"
- Bell, J.S. (1964). "On the Einstein Podolsky Rosen paradox"

## Licença

Este projeto é distribuído sob licença MIT para fins educacionais.

## Contato

Para questões acadêmicas e científicas, consulte sempre físicos profissionais e literatura revisada por pares.

---

**Nota Final**: A ciência avança testando hipóteses falseáveis, não provando teorias infalseáveis. Mantenha o ceticismo científico e a mente aberta.
