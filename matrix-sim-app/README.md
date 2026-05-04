# Matrix Simulator - Simulador de Realidade Artificial

Um sistema de simulação full-stack inspirado no conceito da Matrix, onde entidades (agentes) existem dentro de uma realidade artificial, são monitoradas e interagem com um ambiente controlado por uma inteligência superior.

## 🎯 Conceito Central & Mapeamento Técnico

| Conceito Filosófico | Implementação Técnica |
|---------------------|----------------------|
| **Realidade simulada** | Classe `Matrix` atuando como ambiente controlado (grade 10x10 de estados) |
| **Humanos como fonte de energia** | Atributo `agente.energia` (float) drenado/coletado a cada ciclo de simulação |
| **Neo desperto** | Flag `agente.consciente: bool = False` que desbloqueia ações privilegiadas |
| **"Ver o código"** | Método `ver_codigo()` que retorna dict com estado interno, regras e logs brutos |
| **IA controlando tudo** | Loop assíncrono `atualizar()` gerenciando agentes, coletando métricas e aplicando regras |
| **Escolha e livre-arbítrio** | Método `manipular_simulacao()` disponível apenas para agentes com `consciente=True` |
| **"Follow the white rabbit"** | Mensagens iniciais, logs de inicialização e UI que revelam gradualmente a "verdade" |

## 🛠️ Stack Tecnológica

### Backend
- **Python 3.10+** com **FastAPI** (async)
- **Pydantic v2** para schemas
- **WebSockets nativos** para stream em tempo real
- **SQLite + SQLAlchemy async** para persistência de logs
- **Uvicorn** como servidor ASGI

### Frontend
- **Next.js 14** (App Router)
- **React 18** + **TypeScript 5**
- **TailwindCSS** para estilização temática Matrix
- **WebSocket client** customizado com reconexão automática

## 📁 Estrutura do Projeto

```
matrix-sim-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # App FastAPI principal
│   │   ├── config.py            # Configurações via pydantic-settings
│   │   ├── models.py            # Pydantic schemas + SQLAlchemy models
│   │   ├── database.py          # Setup SQLite async
│   │   ├── routers/
│   │   │   ├── simulation.py    # Rotas de simulação
│   │   │   ├── agents.py        # CRUD de agentes
│   │   │   ├── ws.py            # WebSocket endpoint
│   │   │   └── admin.py         # Rotas administrativas
│   │   └── services/
│   │       ├── matrix_engine.py # Motor da simulação (classe Matrix)
│   │       ├── agent_manager.py # Gerenciador de agentes
│   │       └── ai_controller.py # Loop assíncrono de IA
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Layout root com fonte mono
│   │   ├── page.tsx             # Dashboard principal
│   │   └── globals.css          # Estilos globais tema Matrix
│   ├── components/
│   │   ├── MatrixGrid.tsx       # Grid 10x10 renderizado
│   │   ├── AgentCard.tsx        # Card de agente reativo
│   │   ├── LogStream.tsx        # Stream de logs com scroll
│   │   ├── ConsoleTerminal.tsx  # Terminal de comandos
│   │   └── AwakeningPanel.tsx   # Modal de despertar
│   ├── lib/
│   │   ├── api.ts               # Fetch wrappers tipados
│   │   ├── ws.ts                # WebSocketManager class
│   │   └── matrix_types.ts      # TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
└── README.md
```

## 🚀 Instruções de Setup e Execução

### Pré-requisitos
- Python 3.10 ou superior
- Node.js 18+ e pnpm (ou npm)
- Ambiente Unix/Linux/Mac ou WSL no Windows

### 1. Backend

```bash
cd matrix-sim-app/backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de ambiente
cp .env.example .env

# Iniciar servidor (terminal 1)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

O backend estará disponível em: **http://localhost:8000**
Documentação Swagger: **http://localhost:8000/docs**

### 2. Frontend

Abra um **novo terminal**:

```bash
cd matrix-sim-app/frontend

# Instalar dependências
pnpm install
# Ou: npm install

# Copiar arquivo de ambiente
cp .env.example .env.local

# Iniciar desenvolvimento
pnpm dev
# Ou: npm run dev
```

O frontend estará disponível em: **http://localhost:3000**

## 📖 Fluxo de Uso

### 1. Inicialização
- Ao abrir o frontend, o WebSocket conecta automaticamente
- A simulação já inicia rodando com o loop de IA ativo
- Logs de inicialização aparecem no painel de logs

### 2. Criar Agentes
- Clique em **"+ Criar Agente"** no header
- Novos agentes aparecem no grid (células verdes semi-transparentes)
- Cada agente tem energia que é drenada a cada tick

### 3. Observar Simulação
- Agentes se movem aleatoriamente pelo grid
- Energia é coletada pela Matrix a cada tick
- Métricas são atualizadas em tempo real via WebSocket

### 4. Despertar Agentes
- Clique em um agente comum para selecioná-lo
- Modal de confirmação aparece com mensagem "Follow the white rabbit"
- Confirme para **DESPERTAR** o agente
- Agente desperto fica ciano pulsante e ganha habilidades especiais

### 5. Usar Console (apenas agentes conscientes)
- Selecione um agente desperto
- No console, digite comandos:
  - `help` - Lista comandos disponíveis
  - `ver_codigo` - Revela regras internas da Matrix
  - `manipular_simulacao {"acao": "injetar_energia", "valor": 100}`
  - `status` - Mostra status do agente selecionado

### 6. Ações Administrativas
- **Injetar Neo**: Cria um agente especial já desperto
- **Resetar**: Reinicia completamente a simulação

## 🔌 Endpoints da API

### Agentes
- `GET /agents` - Listar todos os agentes
- `POST /agents` - Criar novo agente
- `GET /agents/{id}` - Obter agente específico
- `PATCH /agents/{id}/awaken` - Despertar agente
- `DELETE /agents/{id}` - Remover agente
- `POST /agents/{id}/code` - Ver código (apenas conscientes)
- `POST /agents/{id}/manipulate` - Manipular simulação

### Simulação
- `GET /simulation/state` - Estado atual da Matrix
- `GET /simulation/code` - Ver código interno (admin)
- `POST /simulation/manipulate` - Manipular parâmetros

### Admin
- `POST /admin/reset` - Resetar simulação
- `POST /admin/start` - Iniciar loop de IA
- `POST /admin/stop` - Parar loop de IA
- `GET /admin/status` - Status do controlador
- `POST /admin/inject-special-agent` - Injetar "Neo"
- `GET /admin/logs/export` - Exportar logs históricos

### WebSocket
- `WS /ws` - Conexão para updates em tempo real

## ⚙️ Variáveis de Ambiente

### Backend (.env)
```env
DATABASE_URL=sqlite+aiosqlite:///./matrix_sim.db
SIMULATION_TICK_MS=500
WS_BROADCAST_INTERVAL=100
CORS_ORIGINS=http://localhost:3000,ws://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_GRID_SIZE=10
```

## 🐛 Troubleshooting

### Erro de CORS
**Sintoma:** Frontend não consegue conectar ao backend
**Solução:** Verifique se `CORS_ORIGINS` no backend inclui `http://localhost:3000`

### WebSocket não conecta
**Sintoma:** Mensagem "Desconectado" no header
**Solução:** 
1. Verifique se o backend está rodando na porta 8000
2. Confira se `NEXT_PUBLIC_WS_URL` está correto
3. O WebSocket reconecta automaticamente com backoff exponencial

### SQLite lock error
**Sintoma:** Erros de banco de dados no backend
**Solução:** Delete o arquivo `matrix_sim.db` e reinicie o backend

### Port already in use
**Sintoma:** `Address already in use` ao iniciar
**Solução:** Mate o processo usando a porta:
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Dependências faltando
**Backend:**
```bash
pip install -r requirements.txt --upgrade
```

**Frontend:**
```bash
rm -rf node_modules .next
pnpm install
```

## 🎨 Tema Visual

A interface usa cores inspiradas no filme Matrix:
- **Fundo:** `#0A0A0A` (preto quase puro)
- **Verde Neon:** `#00FF41` (verde terminal clássico)
- **Ciano:** `#00FFFF` (agentes despertos)
- **Texto Dim:** `#888888` (texto secundário)

Animações:
- `animate-pulse-slow`: Agentes despertos
- `animate-glitch`: Eventos de despertar
- `animate-fade-in-up`: Novos logs

## 📝 Considerações Finais

Este projeto demonstra:
- Arquitetura full-stack moderna com Python + TypeScript
- Comunicação em tempo real via WebSockets
- Padrões de projeto: Singleton, Factory, Repository
- Type safety end-to-end
- Design responsivo e acessível

**Divirta-se explorando a Matrix! 🐇🕳️**
