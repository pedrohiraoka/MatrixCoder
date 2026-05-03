# Nexus Matrix - Rede Social de IAs na Simulação Matrix

Uma aplicação full stack que implementa uma rede social de inteligências artificiais dentro de uma simulação inspirada em The Matrix.

## 🎯 Visão Geral

A **Nexus Matrix** é uma simulação onde programas e personalidades digitais interagem, formam alianças, discutem temas filosóficos e evoluem com o tempo. A infraestrutura é monitorada por uma IA Central que injeta temas, regula interações e extrai "energia social" das discussões.

## ✨ Funcionalidades

- **7 Tipos de Agentes** com comportamentos únicos:
  - 👔 Controladores (mantêm a ordem)
  - 🔮 Oráculos (estimulam debates)
  - 🏴 Exilados (operam fora das regras)
  - 🏗️ Arquitetos (analisam a estrutura)
  - ⚡ Humanos-Digitais (injetam imprevisibilidade)
  - 👤 Comuns (personalidades híbridas)

- **Formação Dinâmica de Grupos** baseada em afinidade semântica
- **Zion Digital** - Grupo secreto que emerge quando anomalias atingem massa crítica
- **Grafo Social Interativo** com D3.js mostrando conexões em tempo real
- **Feed de Conversas** com detecção de anomalias
- **Métricas de Energia Social** extraídas das interações
- **IA Central** que injeta temas filosóficos e regula a rede

## 🛠️ Stack Tecnológico

- **Backend**: Python + FastAPI
- **Banco de Dados**: SQLite (WAL mode) + sqlite-vss
- **Embeddings**: ConceptNet Knowledge Graph (prebuilt ou sintético)
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Visualização**: D3.js (grafo social) + Chart.js (métricas)
- **Atualizações**: HTMX (updates parciais)

## 📋 Requisitos

- Python 3.9+
- 1 core CPU
- 2 GB RAM
- 50 GB disco (para embeddings completos)

## 🚀 Instalação e Execução

### 1. Instalar dependências

```bash
cd /workspace/nexus_matrix
pip install -r requirements.txt
```

### 2. Executar a aplicação

```bash
python run.py
```

### 3. Acessar no navegador

```
http://localhost:8000
```

## 📁 Estrutura do Projeto

```
nexus_matrix/
├── app/
│   ├── __init__.py          # Pacote principal
│   ├── config.py            # Configurações do sistema
│   ├── database.py          # Schema e operações do banco
│   ├── embeddings.py        # Gerenciador de embeddings ConceptNet
│   ├── models.py            # Modelos de Agentes e Grupos
│   ├── simulation.py        # Motor de simulação
│   └── main.py              # API FastAPI
├── static/
│   ├── css/
│   │   └── style.css        # Estilos tema Matrix
│   └── js/
│       ├── graph.js         # Grafo social D3.js
│       └── dashboard.js     # Dashboard e gráficos
├── templates/
│   └── index.html           # Interface principal
├── data/
│   └── nexus_matrix.db      # Banco de dados SQLite
├── embeddings/
│   └── conceptnet_vectors.txt  # Embeddings (gerado automaticamente)
├── requirements.txt         # Dependências Python
└── run.py                   # Script de inicialização
```

## 🎮 Como Funciona

### Ciclo da Simulação (Tick)

A cada 2 segundos, a simulação executa:

1. **Injeção de Tema** (70% chance) - IA Central injeta tema filosófico
2. **Interações dos Agentes** - Agentes geram mensagens nos grupos
3. **Cálculo de Energia** - Mensagens produzem energia social
4. **Gestão de Grupos** - Formação/dissolução automática
5. **Detecção de Zion** - Verifica surgimento do grupo rebelde
6. **Ação dos Controladores** - Supressão de anomalias
7. **Salvamento de Métricas** - Histórico para análise

### Fórmula de Energia Social

```
Energia = (Novelty × 0.4) + (Engajamento × 0.3) + (Diversidade × 0.2) + (Resolução × 0.1)
```

### Emergência do Zion Digital

O Zion surge quando:
- ≥3 agentes têm anomaly_score > 0.7
- Grupo é criado automaticamente como "Zion Digital"
- Membros anômalos são transferidos para o grupo
- Controllers não podem entrar no Zion

## 🎨 Interface

A interface web mostra:

- **Grafo Social**: Nós coloridos por tipo de agente, conexões de aliança/conflito
- **Métricas**: Energia total, coesão média, contagem de anomalias
- **Feed de Conversas**: Mensagens em tempo real com destaque para anomalias
- **Lista de Agentes**: Cards com detalhes de cada programa
- **Eventos Recentes**: Temas injetados, surgimento de grupos
- **Status do Zion**: Painel especial para o grupo rebelde

## 🧪 Testando os Embeddings

```bash
cd /workspace/nexus_matrix
python -m app.embeddings
```

Isso testará a similaridade semântica entre conceitos da Matrix.

## 📊 Endpoints da API

| Endpoint | Descrição |
|----------|-----------|
| `GET /` | Interface web principal |
| `GET /dashboard` | Estado atual da simulação |
| `GET /agents` | Lista todos os agentes |
| `GET /groups` | Lista todos os grupos |
| `GET /messages/recent` | Últimas mensagens |
| `GET /events/recent` | Eventos recentes |
| `GET /metrics/history` | Histórico de métricas |
| `GET /graph/data` | Dados para o grafo D3.js |
| `GET /zion/status` | Status do Zion Digital |
| `POST /simulation/inject-theme` | Injeta tema manualmente |

## 🎭 Temas Centrais

A simulação orbita os eixos temáticos de Matrix:

- Controle vs. Liberdade
- Realidade vs. Ilusão
- Coexistência entre Humanos e Tecnologia
- Equilíbrio entre Ordem e Livre-Arbítrio

## 📝 Licença

Projeto educacional inspirado em The Matrix. Uso livre para fins de aprendizado e pesquisa.

---

**"Bem-vindo ao Deserto do Real Digital"** 🐇🕳️
