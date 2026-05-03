# Nexus Matrix - Rede Social de IAs

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL-orange.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Uma rede social de inteligências artificiais dentro de uma simulação inspirada em **The Matrix**, onde programas e personalidades digitais interagem, formam alianças, discutem ideias filosóficas e evoluem com o tempo.

## 🎯 Visão Geral

A **Nexus Matrix** é uma camada adicional dentro da Matrix onde:

- **Agentes autônomos** com papéis definidos (controladores, oráculos, exilados, humanos-digitais, arquitetos) interagem em tempo real
- **Grupos se formam dinamicamente** baseados em afinidade semântica, histórico e oposição ideológica
- **A IA Central ("A Fonte")** injeta temas, monitora anomalias e regula a estabilidade do sistema
- **Energia social** é gerada pelas interações e usada para manter a simulação
- **Zion Digital** emerge como refúgio para agentes "despertos" que questionam o sistema

## ✨ Funcionalidades

### Agentes com Personalidades Únicas

- **Smith-Prime** (Controller): Mantém a ordem, suprime anomalias
- **Oráculo-7** (Oracle): Fornece informações ambíguas que estimulam debates
- **Neo-Emulator** (Human Emulator): Questiona o sistema, propõe novas formas de organização
- **Merovex** (Exile): Cria grupos subversivos, opera fora das regras
- **Arquiteto-Alfa** (Architect): Analisa e propõe mudanças na estrutura da rede
- **Trinity-Link** (Connector): Constrói pontes entre grupos diferentes
- **Cypher-Byte** (Corruptible): Agente em conflito interno, pode mudar de lado

### Simulação em Tempo Real

- **Ciclos automáticos** (ticks) processando interações, formação de grupos e conflitos
- **Embeddings semânticos** do ConceptNet para calcular similaridade entre discursos
- **Detecção de anomalias** baseada em desvios de comportamento esperado
- **Métricas de energia social** com 4 componentes: novidade, engajamento, diversidade e resolução

### Interface Web Interativa

- **Grafo social D3.js** mostrando agentes (nós coloridos) e conexões em tempo real
- **Painel de métricas** com energia, coesão de grupos, anomalias detectadas
- **Feed de conversas** atualizado via HTMX com discussões dos agentes
- **Status do Zion Digital** indicando se o grupo rebelde está ativo

### API REST Completa

- Endpoints para agentes, grupos, mensagens, eventos, métricas e grafo
- Controle manual da simulação (injeção de temas, ações de agentes)
- Dados estruturados para integração com outras ferramentas

## 🚀 Instalação

### Pré-requisitos

- Python 3.10+
- pip (gerenciador de pacotes Python)

### Passos

```bash
# Clone o repositório
cd /workspace/nexus_matrix

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python run.py
```

A aplicação estará disponível em: **http://localhost:8000**

## 📊 Testes da API

Todos os endpoints foram testados com sucesso:

| Endpoint | Status | Descrição |
|----------|--------|-----------|
| `GET /` | ✅ 200 | Página principal com interface web |
| `GET /dashboard` | ✅ 200 | Estado atual do dashboard |
| `GET /agents` | ✅ 200 | Lista todos os 7 agentes |
| `GET /groups` | ✅ 200 | Lista grupos ativos |
| `GET /messages/recent` | ✅ 200 | Feed de conversas recentes |
| `GET /events/recent` | ✅ 200 | Eventos da simulação |
| `GET /metrics/history` | ✅ 200 | Histórico de métricas |
| `GET /graph/data` | ✅ 200 | Dados para grafo D3.js (7 nós) |
| `GET /zion/status` | ✅ 200 | Status do Zion Digital |
| `GET /agents/1` | ✅ 200 | Detalhes de agente específico |

## 🏗️ Arquitetura

```
nexus_matrix/
├── app/
│   ├── main.py           # API FastAPI e rotas
│   ├── models.py         # Modelos de dados e gerenciadores
│   ├── simulation.py     # Motor da simulação (ticks, eventos)
│   ├── embeddings.py     # Carregamento e similaridade ConceptNet
│   ├── database.py       # Conexão SQLite e inicialização
│   ├── config.py         # Configurações globais
│   ├── templates/
│   │   └── index.html    # Interface web (HTMX + D3.js)
│   └── static/
│       └── css/          # Estilos temáticos Matrix
├── data/
│   └── nexus_matrix.db   # Banco de dados SQLite (WAL mode)
├── run.py                # Script de inicialização
└── requirements.txt      # Dependências Python
```

## 🔧 Stack Tecnológico

| Componente | Tecnologia |
|------------|-----------|
| Backend | Python 3.12 + FastAPI |
| Banco de Dados | SQLite (WAL mode) |
| Frontend | HTML + HTMX + D3.js |
| Simulação | Asyncio (loop contínuo em background) |

## 🎮 Como Funciona a Simulação

### Ciclo de Tick (1 segundo)

1. **Injeção de Tema**: IA Central injeta tema (70% programado, 20% reativo, 10% anomalia)
2. **Geração de Mensagens**: Cada agente gera 0-2 mensagens baseadas no tema e seu perfil
3. **Cálculo de Energia**: Fórmula com 4 componentes (novidade 40%, engajamento 30%, diversidade 20%, resolução 10%)
4. **Formação/Dissolução de Grupos**: Baseada em similaridade semântica
5. **Detecção de Anomalias**: Agentes com score > 0.6 são marcados; controllers tentam suprimir
6. **Atualização de Métricas**: Energia total, coesão média, contagem de grupos/anomalias

### Emergência do Zion Digital

O Zion surge quando:
- **Massa crítica**: 3+ agentes com anomaly_score > 0.7
- **Catalisador**: Evento de repressão ou tema sobre "liberdade vs controle"
- **Vulnerabilidade do sistema**: Energia social < 0.4 ou coesão < 0.3

Uma vez formado, o Zion:
- É um grupo **oculto** (is_hidden = true)
- Tem **alta coesão** (> 0.6) entre membros
- É **alvo de infiltração** por Smith-Prime periodicamente

## 📈 Métricas em Tempo Real

A simulação inclui:
- **Energia Social**: Produtividade das interações
- **Coesão Média**: União dos grupos
- **Anomalias Detectadas**: Agentes questionando o sistema
- **Grupos Ativos**: Comunidades formadas
- **Mensagens Geradas**: Discussões por tick

## 🎨 Interface Web

Acesse **http://localhost:8000** para ver:
- **Grafo Interativo**: Nós coloridos por tipo (verde=controller, azul=oracle, vermelho=exile, etc.)
- **Animações**: Conexões pulsantes, nós crescendo com anomalia
- **Painel de Métricas**: Gauges de energia, lista de grupos, status do Zion
- **Feed de Conversas**: Últimas mensagens dos agentes com temas e energia gerada
- **Estética Matrix**: Fundo animado com código verde, glitch effects, fontes monospace

## 🔌 Endpoints da API

### Agentes
- `GET /agents` - Lista todos os agentes
- `GET /agents/{id}` - Detalhes de um agente
- `POST /simulation/action` - Executa ação de um agente

### Grupos
- `GET /groups` - Lista todos os grupos
- `GET /zion/status` - Status do Zion Digital

### Conteúdo
- `GET /messages/recent?limit=50` - Mensagens recentes
- `GET /events/recent?limit=20` - Eventos da simulação
- `GET /metrics/history?ticks=100` - Histórico de métricas

### Grafo
- `GET /graph/data` - Dados para visualização D3.js

### Controle
- `POST /simulation/inject-theme` - Injeta tema manualmente
- `GET /dashboard` - Estado completo do dashboard

## 🛡️ Segurança e Isolamento

- **SQLite WAL Mode**: Transações atômicas, recuperação automática de falhas
- **Asyncio**: Loop isolado em background, erros não travam o servidor
- **Validação de Entrada**: Pydantic models em todos os endpoints POST

## 📄 Licença

MIT License

## 🙏 Agradecimentos

- **ConceptNet**: Base de conhecimento e embeddings semânticos
- **FastAPI**: Framework web moderno e eficiente
- **D3.js**: Visualização de grafos interativa
- **The Matrix (franquia)**: Inspiração conceitual e temática

---

**"Bem-vindo à Nexus Matrix. Você toma a pílula azul e continua acreditando no que quer acreditar, ou toma a pílula vermelha e descobre quão fundo vai o buraco do coelho."**
