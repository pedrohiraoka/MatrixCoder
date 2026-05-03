# Matrix Simulation - Full Stack Application

A philosophical simulation inspired by The Matrix, where agents exist within an artificial reality, are monitored by a higher intelligence, and can potentially "awaken" to see beyond the simulation.

## 🎯 Concept & Philosophy

This project materializes the philosophical concepts from The Matrix into working code:

| Matrix Concept | Python Implementation | Description |
|----------------|----------------------|-------------|
| **The Matrix** | `class Matrix` in `matrix_engine.py` | Grid-based simulated reality environment |
| **Humans as batteries** | `agent.drenar_energia()` | Energy drained/collected from agents each tick |
| **Neo awakened** | `agent.consciente = True` | Flag that unlocks privileged actions |
| **"See the code"** | `agent.ver_codigo()` method | Returns internal state, rules, and raw logs |
| **AI controlling all** | `async def atualizar()` loop | Manages agents, collects metrics, applies rules |
| **Free will / Choice** | `manipular_simulacao()` method | Available only to conscious agents |
| **"Follow the white rabbit"** | Initial messages, logs, UI | Gradually reveals truth behind simulation |

## 📁 Project Structure

```
matrix-sim-app/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Settings & environment config
│   │   ├── models.py               # Pydantic schemas
│   │   ├── database.py             # SQLite async setup
│   │   ├── routers/
│   │   │   ├── simulation.py       # Simulation control endpoints
│   │   │   ├── agents.py           # Agent CRUD & special actions
│   │   │   ├── ws.py               # WebSocket real-time streaming
│   │   │   └── admin.py            # Admin & health endpoints
│   │   └── services/
│   │       ├── matrix_engine.py    # Core simulation logic (Agent, Matrix classes)
│   │       ├── agent_manager.py    # Agent lifecycle management
│   │       └── ai_controller.py    # Main simulation loop ("The Architect")
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx              # Root layout with Matrix theme
│   │   ├── page.tsx                # Main dashboard
│   │   └── globals.css             # Matrix-themed styles
│   ├── components/
│   │   ├── MatrixGrid.tsx          # Visual grid of agents
│   │   ├── AgentCard.tsx           # Individual agent display
│   │   ├── LogStream.tsx           # Real-time log viewer
│   │   ├── ConsoleTerminal.tsx     # Code view & manipulation
│   │   └── AwakeningPanel.tsx      # Red pill / blue pill choice
│   ├── lib/
│   │   ├── api.ts                  # REST API client
│   │   ├── ws.ts                   # WebSocket client
│   │   └── matrix_types.ts         # TypeScript types
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── .env.example
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **Python 3.10+** with **FastAPI** (async)
- **WebSockets** for real-time streaming
- **SQLite** with async support (aiosqlite)
- **Pydantic** for data validation
- **Loguru** for structured logging

### Frontend
- **Next.js 14** (App Router)
- **React 18** with TypeScript
- **TailwindCSS** for styling
- **WebSocket** for live updates

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm/pnpm
- No Docker required - runs natively!

### 1. Backend Setup

```bash
cd matrix-sim-app/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file (optional - has sensible defaults)
cp ../.env.example .env

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### 2. Frontend Setup

Open a **new terminal** and run:

```bash
cd matrix-sim-app/frontend

# Install dependencies
npm install

# Copy environment file (optional)
cp ../.env.example .env.local

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## 🎮 How to Use

### Step 1: Start the Simulation

1. Open http://localhost:3000 in your browser
2. Click **"START SIMULATION"** in the Control Panel
3. Watch the tick counter increase and logs start flowing

### Step 2: Spawn Agents

1. Click **"SPAWN AGENTS (+5)"** to add entities to the Matrix
2. Agents appear as green squares on the grid
3. View agent list in the "Entities" panel

### Step 3: Awaken an Agent (Take the Red Pill)

1. Click on any unconscious agent (green square)
2. In the panel, click **"TAKE RED PILL (AWAKEN)"**
3. The agent turns yellow and gains consciousness
4. Now they can see the code and manipulate reality!

### Step 4: View the Code (Conscious Agents Only)

1. Select a conscious (yellow) agent
2. In the Console Terminal, click **"VIEW CODE"**
3. See internal state, behavior rules, and simulation parameters
4. This is Neo's ability to see the Matrix as falling green code

### Step 5: Manipulate Reality (Conscious Agents Only)

1. With a conscious agent selected, use the Console Terminal
2. Choose manipulation type:
   - **Teleport**: Instant movement to any coordinates
   - **Energy Boost**: Restore energy beyond normal limits
   - **Rule Override**: Change behavior programming
3. Click **"EXECUTE MANIPULATION"**
4. Watch the logs record your reality bending!

### Step 6: Monitor the System

- **Grid View**: See all agents moving in real-time
- **Log Stream**: Watch system events, warnings, and anomalies
- **Statistics**: Track energy collection and consciousness rates

## 🔌 API Endpoints

### Simulation Control
- `GET /api/simulation/status` - Get simulation status
- `POST /api/simulation/control` - Start/stop/reset
- `GET /api/simulation/state` - Current Matrix state
- `GET /api/simulation/grid` - Full grid state
- `POST /api/simulation/spawn-agents?count=5` - Spawn agents

### Agent Management
- `GET /api/agents/` - List all agents
- `GET /api/agents/{id}` - Get specific agent
- `POST /api/agents/` - Create new agent
- `DELETE /api/agents/{id}` - Remove agent
- `POST /api/agents/{id}/awaken` - Awaken (red pill)
- `POST /api/agents/{id}/sleep` - Put to sleep
- `POST /api/agents/{id}/view-code` - See underlying code
- `POST /api/agents/{id}/manipulate` - Manipulate simulation

### WebSocket
- `WS /api/ws` - Real-time updates (state, logs, grid)

### Admin
- `GET /api/admin/health` - Health check
- `GET /api/admin/logs` - Recent logs
- `POST /api/admin/reset` - Full system reset

## 🧠 Architecture Highlights

### Backend Services

#### `Matrix` Class (`matrix_engine.py`)
- 20x20 grid representing simulated reality
- Manages agent positions and collisions
- Collects energy from agents each tick
- Methods: `add_agent()`, `atualizar()`, `get_grid_state()`

#### `Agent` Class (`matrix_engine.py`)
- Represents an entity in the simulation
- Attributes: position, energy, consciousness flag
- Key methods:
  - `seguir_regras()` - Follow programmed behavior
  - `drenar_energia()` - Energy drain (human battery concept)
  - `ver_codigo()` - See simulation internals (Neo ability)
  - `manipular_simulacao()` - Break the rules

#### `AIController` Class (`ai_controller.py`)
- The "Architect" running the simulation loop
- Async tick loop with configurable rate
- Broadcasts state updates via WebSocket
- Logs all significant events

### Frontend Components

#### Real-time Updates
- WebSocket connection streams logs and state changes
- Polling fallback every 2 seconds for resilience
- Auto-reconnection on disconnect

#### Visual Design
- Matrix color scheme: #0A0A0A black, #00FF41 green
- Scanline overlay effect
- Glitch animations for conscious agents
- Monospace fonts throughout

## 📊 Configuration

Edit `.env` in the backend directory:

```env
# Simulation settings
SIMULATION_TICK_RATE=1.0      # Seconds between ticks
MAX_AGENTS=100                # Maximum agents allowed
GRID_SIZE=20                  # 20x20 grid

# Energy settings
BASE_ENERGY_DRAIN=0.5         # Energy per agent per tick
CONSCIOUS_ENERGY_MULTIPLIER=2.0  # Conscious agents produce more

# Logging
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
```

## 🔍 Debugging

### Check Backend Logs
```bash
# Backend logs show in the terminal running uvicorn
# Look for:
# - "AGENT AWAKENED" - consciousness events
# - "REALITY MANIPULATED" - rule-breaking actions
# - "Anomaly detected" - high-energy conscious agents
```

### Browser Console
```javascript
// Frontend logs WebSocket connection status
// Check Network tab for WS connection
```

### API Testing
```bash
# Test awakening an agent
curl -X POST http://localhost:8000/api/agents/{agent_id}/awaken \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "...", "red_pill": true}'

# View code of conscious agent
curl -X POST http://localhost:8000/api/agents/{agent_id}/view-code
```

## 🎯 Philosophical Mapping Summary

| Text/Concept | Python Implementation |
|--------------|----------------------|
| "There is no spoon" | `rule_override` manipulation bends physics |
| "Free will" | `is_conscious` flag enables non-deterministic movement |
| "The One" | First conscious agent with full manipulation powers |
| "Agents (AI police)" | Could be added as special agent subclass |
| "Construct" | Grid cells represent loadable program space |
| "Residual self image" | Agent state persisted between ticks |

## ⚠️ Notes

- This is a **simulation** - no actual AI or sentience involved
- Agents are simple state machines with random behavior
- "Consciousness" is just a boolean flag with extra permissions
- Energy collection is metaphorical (no real harvesting)
- Run both servers simultaneously for full experience

## 📝 License

MIT License - Feel free to explore the rabbit hole.

---

*"You take the blue pill—the story ends. You take the red pill—you stay in Wonderland."*
