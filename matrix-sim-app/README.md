# 🕳️ Matrix Simulation App

> *"Welcome to the real world."*

Uma plataforma web full-stack interativa que integra **Machine Learning**, **Manipulação de Dados em escala** e **Criptografia**, tudo envolto em uma interface temática "Matrix" com chuva de código verde, painéis de streaming e logs em tempo real.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    MATRIX SIMULATION APP                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Frontend   │◄───────►│    Backend   │                 │
│  │   Next.js 14 │   WS    │   FastAPI    │                 │
│  │   React + TS │  HTTP   │   Python 3.11│                 │
│  └──────────────┘         └──────────────┘                 │
│         │                       │                           │
│         │                       ▼                           │
│         │              ┌─────────────────┐                 │
│         │              │   SQLAlchemy    │                 │
│         │              │   SQLite (dev)  │                 │
│         │              └─────────────────┘                 │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Componentes da Interface               │   │
│  │  • MatrixRain (Canvas animation)                    │   │
│  │  • MLPanel (Isolation Forest)                       │   │
│  │  • DataPanel (Pandas transformations)               │   │
│  │  • CryptoPanel (Fernet encryption)                  │   │
│  │  • LogStream (WebSocket real-time)                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔮 Os Três Pilares da Matrix

### 1. 👁️ O Agente (Machine Learning/IA)
- **Algoritmo**: Isolation Forest (scikit-learn)
- **Função**: Detectar "glitches" na Matrix (anomalias em dados sintéticos)
- **Conexão temática**: Assim como os Agentes detectam irregularidades na Matrix, o Isolation Forest identifica pontos fora do padrão em fluxos de dados
- **Endpoint**: `POST /api/ml/simulate`

### 2. 🧬 O Construto (Manipulação de Dados)
- **Tecnologia**: Pandas + NumPy
- **Função**: Transformar, normalizar e agregar fluxos massivos de dados sintéticos
- **Conexão temática**: O Construto é o espaço branco onde Neo carrega programas e dados; aqui processamos os "dados brutos da Matrix"
- **Endpoint**: `POST /api/data/process`

### 3. 🔐 O Cofre (Criptografia/Segurança)
- **Algoritmo**: Fernet (AES-CBC 128-bit + HMAC SHA256)
- **Função**: Criptografar e descriptografar payloads de simulação
- **Conexão temática**: Protege os segredos da Matrix contra interceptação, assim como Cypher negociava seus dados criptografados
- **Endpoints**: `POST /api/crypto/encrypt`, `POST /api/crypto/decrypt`

---

## 📁 Estrutura do Projeto

```
/matrix-sim-app
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings & environment
│   │   ├── models.py            # SQLModel database models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── database.py          # DB session management
│   │   ├── routers/
│   │   │   ├── ml.py            # ML simulation endpoints + WS
│   │   │   ├── data.py          # Data processing endpoints
│   │   │   ├── crypto.py        # Encryption/decryption endpoints
│   │   │   └── ws.py            # WebSocket log streaming
│   │   └── services/
│   │       ├── ml_engine.py     # Isolation Forest logic
│   │       ├── data_processor.py # Pandas transformations
│   │       └── crypto_service.py # Fernet encryption
│   ├── requirements.txt
│   └── Dockerfile.backend
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Dashboard main page
│   │   └── globals.css          # Global styles + Matrix theme
│   ├── components/
│   │   ├── MatrixRain.tsx       # Canvas rain animation
│   │   ├── MLPanel.tsx          # ML simulation UI
│   │   ├── DataPanel.tsx        # Data processing UI
│   │   ├── CryptoPanel.tsx      # Crypto operations UI
│   │   └── LogStream.tsx        # Real-time log viewer
│   ├── lib/
│   │   ├── api.ts               # API client functions
│   │   └── ws.ts                # WebSocket client class
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── Dockerfile.frontend
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Setup e Execução

### Pré-requisitos
- Docker e Docker Compose instalados
- OU Python 3.10+ e Node.js 18+ para execução local

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
cd matrix-sim-app

# Copie o arquivo de ambiente
cp .env.example .env

# Inicie todos os serviços
docker compose up --build

# Acesse:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Opção 2: Execução Local

#### Backend
```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar .env
cp ../.env.example .env

# Rodar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Criar .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local

# Rodar em desenvolvimento
npm run dev
```

---

## 📡 Endpoints da API

### Machine Learning
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/ml/simulate` | Gera dados sintéticos e detecta anomalias |
| WS | `/ws/simulate` | Stream em tempo real de simulações |

**Exemplo de Request:**
```json
{
  "n_samples": 1000,
  "n_features": 5,
  "contamination": 0.1
}
```

### Data Processing
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/data/process` | Processa e transforma dados |
| GET | `/api/data/stats` | Estatísticas dos dados carregados |

**Exemplo de Request:**
```json
{
  "data": [{"id": 1, "value": 42}],
  "transformations": ["normalize", "aggregate"]
}
```

### Criptografia
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/crypto/encrypt` | Criptografa payload |
| POST | `/api/crypto/decrypt` | Descriptografa token |
| GET | `/api/crypto/validate/{token}` | Valida token Fernet |

**Exemplo de Request:**
```json
{
  "payload": "Mensagem secreta"
}
```

### WebSocket
| Endpoint | Descrição |
|----------|-----------|
| `/ws/logs` | Stream de logs em tempo real |
| `/ws/stream` | Stream genérico de dados |

---

## 🎨 Tema Visual

A interface segue a estética icônica de Matrix:

- **Cores**:
  - Fundo: `#0A0A0A` (preto quase absoluto)
  - Verde principal: `#00FF41` (verde terminal)
  - Verde escuro: `#008F11` (bordas e detalhes)
  - Cinza: `#1F1F1F` (painéis)

- **Efeitos**:
  - Chuva de caracteres katakana + latinos em Canvas
  - Texto com glow neon
  - Bordas sutis com sombra verde
  - Fontes monoespaçadas (Courier New)

---

## 🧪 Testando os Módulos

### 1. Testar ML Simulation
```bash
curl -X POST http://localhost:8000/api/ml/simulate \
  -H "Content-Type: application/json" \
  -d '{"n_samples": 500, "n_features": 3, "contamination": 0.1}'
```

### 2. Testar Data Processing
```bash
curl -X POST http://localhost:8000/api/data/process \
  -H "Content-Type: application/json" \
  -d '{"data": [{"x": 1, "y": 2}, {"x": 3, "y": 4}], "transformations": ["normalize"]}'
```

### 3. Testar Criptografia
```bash
# Encrypt
curl -X POST http://localhost:8000/api/crypto/encrypt \
  -H "Content-Type: application/json" \
  -d '{"payload": "Hello Matrix"}'

# Decrypt (use o resultado do encrypt)
curl -X POST http://localhost:8000/api/crypto/decrypt \
  -H "Content-Type: application/json" \
  -d '{"encrypted_data": "<token_do_encrypt>"}'
```

### 4. Testar WebSocket (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/logs');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

---

## 🛡️ Segurança

- Chave de criptografia deve ser alterada em produção via `.env`
- CORS configurado para `*` em desenvolvimento (restrinja em produção)
- Logs de todas as operações são persistidos no banco de dados
- Validação rigorosa de inputs com Pydantic

---

## 📊 Tecnologias Utilizadas

| Camada | Tecnologia |
|--------|------------|
| Backend | FastAPI, Uvicorn, Python 3.11 |
| Frontend | Next.js 14, React 18, TypeScript |
| ML/IA | scikit-learn, Pandas, NumPy |
| Criptografia | cryptography (Fernet) |
| Banco de Dados | SQLite + SQLModel |
| Real-time | WebSockets |
| Estilização | TailwindCSS |
| Visualização | Recharts, HTML5 Canvas |
| Infra | Docker, Docker Compose |

---

## 🎯 Considerações Finais

Este projeto demonstra a integração prática de três pilares fundamentais da ciência de dados moderna:

1. **ML/IA** para detecção proativa de anomalias
2. **Big Data** para manipulação eficiente de volumes massivos
3. **Segurança** para proteção de informações sensíveis

Tudo isso apresentado em uma interface imersiva que homenageia um dos filmes mais influentes sobre realidade simulada e controle de informação.

*"There is a difference between knowing the path and walking the path."*

---

**Desenvolvido com ☕ e código verde.**
