/**
 * Tipos TypeScript para a aplicação Matrix Simulator.
 * Espelha os schemas Pydantic do backend.
 */

export interface Agente {
  id: string;
  posicao_x: number;
  posicao_y: number;
  energia: number;
  consciente: boolean;
  regras_comportamento?: {
    prob_movimento: number;
    prob_interacao: number;
    limiar_energia: number;
  };
}

export interface CeldaGrid {
  ocupado: boolean;
  agente_id: string | null;
  energia_ambiental: number;
}

export interface MatrixState {
  grid: CeldaGrid[][];
  tempo_simulacao: number;
  energia_total_coletada: number;
  agentes_despertos: number;
  ticks_executados: number;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  nivel: 'INFO' | 'WARN' | 'ERROR' | 'AWAKEN';
  mensagem: string;
  contexto?: Record<string, any>;
}

export interface MensagemWS {
  type: 'TICK' | 'LOG' | 'AGENTE_UPDATE' | 'ERROR' | 'PONG' | 'LOGS_BATCH';
  payload: any;
}

export interface Metricas {
  tempo_simulacao: number;
  energia_total_coletada: number;
  agentes_despertos: number;
  ticks_executados: number;
}

export interface WSPayload {
  grid?: CeldaGrid[][];
  agentes?: Agente[];
  metricas?: Metricas;
  log?: LogEntry;
  logs?: LogEntry[];
}

export interface CriarAgenteRequest {
  posicao_x?: number;
  posicao_y?: number;
  energia?: number;
}

export interface ManipularSimulacaoRequest {
  acao: string;
  params?: Record<string, any>;
}

export interface RespostaManipulacao {
  sucesso: boolean;
  mensagem: string;
  dados?: Record<string, any>;
}

export interface WebSocketState {
  connected: boolean;
  error: string | null;
  grid: CeldaGrid[][];
  agentes: Agente[];
  logs: LogEntry[];
  metricas: Metricas | null;
}
