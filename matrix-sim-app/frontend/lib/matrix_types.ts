/**
 * TypeScript types for Matrix Simulation frontend.
 * Mirrors the Pydantic models from the backend.
 */

export interface Agent {
  id: string;
  name: string | null;
  position_x: number;
  position_y: number;
  energy: number;
  is_conscious: boolean;
  status: 'normal' | 'awake' | 'disconnected';
  created_at: string;
  last_updated: string;
}

export interface GridCell {
  x: number;
  y: number;
  has_agent: boolean;
  agent_id: string | null;
  is_conscious: boolean;
  energy_level: number;
}

export interface GridState {
  tick: number;
  dimensions: number;
  cells: GridCell[];
}

export interface MatrixState {
  tick: number;
  total_agents: number;
  conscious_agents: number;
  total_energy_collected: number;
  grid_size: number;
  running: boolean;
  start_time: string | null;
}

export interface SimulationStatus {
  running: boolean;
  tick_rate: number;
  subscribers: number;
  log_buffer_size: number;
  matrix_state: MatrixState;
  agent_stats: AgentStatistics;
}

export interface AgentStatistics {
  total_agents: number;
  conscious_count: number;
  unconscious_count: number;
  conscious_percentage: number;
  average_energy: number;
  average_conscious_energy: number;
  average_unconscious_energy: number;
  max_agents_allowed: number;
}

export interface LogEntry {
  timestamp: string;
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  message: string;
  source: string;
  data?: Record<string, any>;
}

export interface WSMessage {
  type: 'state_update' | 'log_entry' | 'agent_update' | 'grid_update' | 'error' | 'welcome' | 'pong' | 'log_history';
  timestamp: string;
  data: any;
  message?: string;
  instruction?: string;
}

export interface ManipulationRequest {
  manipulation_type: 'teleport' | 'energy_boost' | 'rule_override';
  target_x?: number;
  target_y?: number;
  value?: number;
}
