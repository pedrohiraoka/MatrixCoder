# GvG Simulator - Guild Wars Simulator

Simulador de Guerras de Guildas em tempo real com WebSocket, FastAPI e Next.js 14.

## 🎮 Visão Geral

- **Mundo**: Grid 20x20 com territórios, recursos e perigos
- **Jogadores**: Atributos ouro (gasto/aquisição) e pontos_conquista
- **Guildas**: Sistema completo com Guild Masters desbloqueando poderes estratégicos
- **Tempo Real**: Atualizações via WebSocket a cada 3 segundos
- **Ciclo Dia/Noite**: Muda a cada ~30 segundos, afetando spawns de perigos

## 🛠️ Stack Tecnológica

### Backend
- Python 3.10+
- FastAPI (async)
- Pydantic v2
- SQLAlchemy + SQLite (apenas logs/transações)
- WebSockets nativos

### Frontend
- Next.js 14 (App Router)
- React 18
- TypeScript 5+
- TailwindCSS (tema medieval)

## 📁 Estrutura do Projeto

```
gvg-simulator/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI setup, WebSocket, lifespan
│   │   ├── models.py         # Pydantic v2 schemas
│   │   ├── state.py          # In-memory state (grid, players, guilds)
│   │   ├── game_engine.py    # Async loop, spawns, day/night
│   │   └── database.py       # SQLAlchemy setup
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   └── globals.css
    ├── components/
    │   ├── WorldGrid.tsx     # 20x20 interactive grid
    │   ├── GuildPanel.tsx    # Guild Master strategic panel
    │   ├── EventLog.tsx      # WebSocket feed
    │   └── hooks/useWebSocket.ts
    └── package.json
```

## 🚀 Setup Local

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- pnpm ou npm

### 1. Backend

```bash
cd gvg-simulator/backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em `http://localhost:8000`

**Endpoints úteis:**
- `GET /` - Health check
- `GET /painel_guerra` - Estado completo do mundo
- `POST /player/create` - Criar jogador
- `POST /guild/create` - Criar guilda
- `WS /ws/{player_id}` - WebSocket para tempo real

### 2. Frontend

Em outro terminal:

```bash
cd gvg-simulator/frontend

# Instalar dependências
pnpm install
# ou
npm install

# Rodar em desenvolvimento
pnpm dev
# ou
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

## 🎮 Como Jogar

### 1. Login
- Digite um ID único e nome para seu jogador
- Opcional: Entre em uma guilda existente ou crie uma nova

### 2. Exploração
- Use **Setas** ou **WASD** para mover
- **Espaço** ou clique para coletar recursos
- Recursos dão ouro (💰 Ouro, 🍖 Comida, 🪵 Madeira, ⛏️ Ferro)

### 3. Guild Master (Se criar guilda)
Acesse o **Painel Estratégico** para:
- **Capturar Território** (100 ouro): Conquiste tiles no grid
- **Construir Estrutura** (200 ouro): Torre, Muralha, Mina, Acampamento
- **Declarar Guerra**: Anuncie guerra para outras guildas

### 4. Eventos Globais
A cada ~60 segundos, eventos aleatórios ocorrem:
- ✨ Chuva de Ouro
- ⚔️ Invasão de Monstros
- 📜 Descoberta Antiga
- 🙏 Bênção dos Deuses

## 🔧 Comandos da API

### Criar Jogador
```bash
curl -X POST http://localhost:8000/player/create \
  -H "Content-Type: application/json" \
  -d '{"player_id": "player1", "name": "Aragorn", "guild_rank": "Member"}'
```

### Criar Guilda
```bash
curl -X POST http://localhost:8000/guild/create \
  -H "Content-Type: application/json" \
  -d '{"guild_id": "rangers", "name": "Rangers of the North", "leader_id": "player1"}'
```

### Ver Estado do Mundo
```bash
curl http://localhost:8000/painel_guerra
```

## 📊 Features Implementadas

- ✅ Grid 20x20 com terrenos variados (planície, floresta, montanha, água, castelo)
- ✅ Sistema de recursos (ouro, comida, madeira, ferro)
- ✅ Perigos e monstros (spawn mais frequente à noite)
- ✅ Ciclo dia/noite (~30 segundos)
- ✅ WebSockets para atualizações em tempo real
- ✅ Movimento de jogadores
- ✅ Coleta de recursos
- ✅ Sistema de guildas
- ✅ Painel estratégico para Guild Masters
- ✅ Captura de território
- ✅ Construção de estruturas
- ✅ Declaração de guerra
- ✅ Eventos globais aleatórios
- ✅ Log de eventos persistente (SQLite)
- ✅ Transações financeiras registradas
- ✅ Tema medieval com TailwindCSS
- ✅ Reconexão automática do WebSocket

## 🎨 Temas Medievais

Cores personalizadas no Tailwind:
- `bg-medieval-bg`: #1a1a2e (fundo principal)
- `bg-medieval-dark`: #16213e (painéis)
- `text-medieval-accent`: #e94560 (destaques)
- `border-medieval-gold`: #d4af37 (bordas douradas)

## 🐛 Troubleshooting

### Backend não inicia
- Verifique se Python 3.10+ está instalado: `python --version`
- Recrie o ambiente virtual se necessário

### Frontend não conecta ao WebSocket
- Certifique-se que o backend está rodando na porta 8000
- Verifique o CORS no `backend/app/main.py`

### Erros de dependência
- Backend: `pip install --upgrade pip && pip install -r requirements.txt`
- Frontend: `rm -rf node_modules && pnpm install`

## 📝 Notas

- O estado do jogo é mantido em memória (reinicia ao parar o servidor)
- Apenas logs e transações são persistidos no SQLite
- Ambiente local puro - sem Docker ou containers
- Compatível com Python 3.10+ e Node.js 18+

---

**Divirta-se conquistando territórios e dominando as guerras de guildas!** ⚔️🏰
