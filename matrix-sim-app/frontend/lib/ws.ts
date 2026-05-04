/**
 * Gerenciador de conexão WebSocket para comunicação em tempo real.
 * Inclui reconexão automática e handlers tipados.
 */

import { MensagemWS, WebSocketState, Agente, CeldaGrid, LogEntry, Metricas } from './matrix_types';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

type WSCallback = (state: WebSocketState) => void;

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private state: WebSocketState = {
    connected: false,
    error: null,
    grid: [],
    agentes: [],
    logs: [],
    metricas: null,
  };
  private callbacks: Set<WSCallback> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private reconnectTimer: NodeJS.Timeout | null = null;

  constructor() {
    this.connect();
  }

  private connect(): void {
    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => {
        console.log('[WS] Conectado');
        this.state.connected = true;
        this.state.error = null;
        this.reconnectAttempts = 0;
        this.notify();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: MensagemWS = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('[WS] Erro ao parsear mensagem:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('[WS] Desconectado');
        this.state.connected = false;
        this.notify();
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('[WS] Erro:', error);
        this.state.error = 'Erro na conexão WebSocket';
        this.notify();
      };
    } catch (error) {
      console.error('[WS] Falha ao criar conexão:', error);
      this.state.error = 'Falha ao conectar';
      this.notify();
      this.scheduleReconnect();
    }
  }

  private handleMessage(message: MensagemWS): void {
    switch (message.type) {
      case 'TICK':
        if (message.payload.grid) {
          this.state.grid = message.payload.grid as CeldaGrid[][];
        }
        if (message.payload.agentes) {
          this.state.agentes = message.payload.agentes as Agente[];
        }
        if (message.payload.metricas) {
          this.state.metricas = message.payload.metricas as Metricas;
        }
        break;

      case 'LOG':
        if (message.payload) {
          const logEntry = message.payload as LogEntry;
          this.state.logs = [...this.state.logs, logEntry].slice(-100);
        }
        break;

      case 'LOGS_BATCH':
        if (message.payload.logs) {
          this.state.logs = message.payload.logs as LogEntry[];
        }
        break;

      case 'ERROR':
        this.state.error = message.payload.message || 'Erro desconhecido';
        break;
    }

    this.notify();
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WS] Máximo de tentativas de reconexão atingido');
      this.state.error = 'Falha na reconexão - recarregue a página';
      this.notify();
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    this.reconnectAttempts++;

    console.log(`[WS] Tentando reconectar em ${delay}ms (tentativa ${this.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private notify(): void {
    this.callbacks.forEach((callback) => callback({ ...this.state }));
  }

  public subscribe(callback: WSCallback): () => void {
    this.callbacks.add(callback);
    // Notifica imediatamente com o estado atual
    callback({ ...this.state });

    return () => {
      this.callbacks.delete(callback);
    };
  }

  public send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('[WS] Não é possível enviar - conexão fechada');
    }
  }

  public sendPing(): void {
    this.send({ type: 'PING' });
  }

  public requestLogs(limite: number = 50): void {
    this.send({ type: 'GET_LOGS', limite });
  }

  public getState(): WebSocketState {
    return { ...this.state };
  }

  public disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.state.connected = false;
    this.callbacks.clear();
  }
}

// Singleton
let wsManager: WebSocketManager | null = null;

export function getWebSocketManager(): WebSocketManager {
  if (!wsManager) {
    wsManager = new WebSocketManager();
  }
  return wsManager;
}

// Hook helper para React
export function createWSHook() {
  let currentCallback: ((state: WebSocketState) => void) | null = null;

  return {
    subscribe: (callback: (state: WebSocketState) => void) => {
      currentCallback = callback;
      const manager = getWebSocketManager();
      return manager.subscribe(callback);
    },
    getState: () => getWebSocketManager().getState(),
    send: (data: any) => getWebSocketManager().send(data),
  };
}
