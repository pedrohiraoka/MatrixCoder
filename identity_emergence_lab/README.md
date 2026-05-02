# Identity Emergence Lab – Simulador de Nascimento da Consciência

## 🎭 Visão Geral

Este projeto implementa um sandbox onde 10 agentes idênticos (Tachikomas) desenvolvem personalidades emergentes distintas através de:
- Interação com eventos aleatórios
- Reflexão semântica via ConceptNet
- Propagação seletiva de memórias
- Variações estocásticas controladas no processamento de embeddings

## 🏗️ Arquitetura

### Sistema Tachikoma
1. **Memória Coletiva (The Net)**: SQLite central (`data/collective_memory.db`)
2. **Memória Local (The Ghost)**: JSON por agente (`data/ghost_*.json`)
3. **Sincronização Assíncrona**: Loop asyncio com diff e merge
4. **ConceptNet + Embeddings**: sentence-transformers para similaridade semântica

### Stack Tecnológica
- **Backend**: Python 3.10+ com FastAPI + asyncio
- **Frontend**: Streamlit (escolhido por iteração rápida e integração nativa com data-science)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Banco**: SQLite3

## 📁 Estrutura do Projeto

```
identity_emergence_lab/
├── backend/
│   ├── __init__.py
│   ├── engine.py          # Loop principal, gerenciamento de ciclos
│   ├── agent.py           # Classe Tachikoma
│   ├── memory.py          # Camada de abstração SQLite/JSON
│   ├── semantics.py       # Embeddings e similaridade
│   ├── events.py          # Gerador de eventos
│   └── api.py             # FastAPI server
├── frontend/
│   └── app.py             # Streamlit dashboard
├── data/
│   └── .gitkeep
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🚀 Instalação e Execução

### Opção 1: Docker (Recomendado)

```bash
# Build e run
docker-compose up --build

# Acessar em http://localhost:8501
# API em http://localhost:8000
```

### Opção 2: Manual

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar backend (terminal 1)
cd backend
python -m uvicorn api:app --host 0.0.0.0 --port 8000

# Iniciar frontend (terminal 2)
streamlit run frontend/app.py --server.port 8501
```

### Opção 3: Script Rápido

```bash
# Usar o script de inicialização
python scripts/quickstart.py
```

## ⚙️ Parâmetros Ajustáveis

No arquivo `backend/engine.py`, ajuste:

```python
# Configurações do loop
CYCLE_DURATION = 1.0  # segundos por ciclo
SYNC_INTERVAL = 5     # sincronização a cada N ciclos
NOISE_INTENSITY = 0.05  # intensidade do ruído para divergência (0.0-1.0)
PROPAGATION_THRESHOLD = 0.7  # limiar para propagação de memórias

# Número de agentes
NUM_AGENTS = 10
```

## 📊 Métricas Emergentes

Cada Tachikoma desenvolve arquétipos baseados nos pesos do Ghost:
- **Curiosidade**: Tendência a explorar novos conceitos
- **Medo**: Associação com eventos negativos
- **Conformidade**: Alinhamento com a memória coletiva
- **Pragmatismo**: Foco em eficiência/utilidade
- **Empatia**: Correlação com estados de outros agentes
- **Criatividade**: Combinações conceituais únicas

## 🧪 Testando a Emergência

1. Inicie a simulação
2. Observe o radar chart divergir após ~50 ciclos
3. Use "Reset Network" para testar resiliência das personalidades
4. Exporte logs para análise pós-simulação

## 📝 Notas Técnicas

### Como a Emergência é Garantida

1. **Ruído Controlado**: Injeção de noise no cálculo de similaridade cosseno
   ```python
   similarity += np.random.normal(0, NOISE_INTENSITY)
   ```

2. **Seeds Individuais**: Cada agente tem seed única baseada em ID
   ```python
   np.random.seed(agent_id * 1000 + cycle)
   ```

3. **Interpretação Seletiva**: Agentes filtram memórias coletivas baseado em pesos locais

### Calibração

- **NOISE_INTENSITY baixo (0.01-0.03)**: Divergência lenta, arquétipos sutis
- **NOISE_INTENSITY médio (0.05-0.1)**: Divergência balanceada (recomendado)
- **NOISE_INTENSITY alto (0.15+)**: Divergência rápida, possível instabilidade

### Performance

- Embeddings carregados uma vez no inicialização
- Cache LRU para conceitos frequentes
- Batch processing de reflexões
- Async I/O para não bloquear UI

## 🔧 Troubleshooting

**Erro: "Model not found"**
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**Erro: "Database locked"**
```bash
rm data/collective_memory.db
# Reinicie a simulação
```

**Memória alta**
- Reduza `CACHE_SIZE` em `semantics.py`
- Aumente intervalo de garbage collection

## 📄 Licença

MIT License - Uso livre para pesquisa e educação.
