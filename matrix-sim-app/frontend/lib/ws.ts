/**
 * WebSocket client for real-time Matrix simulation updates.
 * Manages connection, reconnection, and message handling.
 */

import { WSMessage } from './matrix_types';

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api';

export type MessageHandler = (message: WSMessage) => void;
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

export class MatrixWebSocket {
  private ws: WebSocket | null = null;
  private handlers: Set<MessageHandler> = new Set();
  private status: ConnectionStatus = 'disconnected';
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private pingInterval: NodeJS.Timeout | null = null;

  constructor() {}

  /**
   * Connect to the WebSocket server.
   * Automatically attempts to reconnect on disconnection.
   */
  connect(endpoint: string = '/ws'): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.status = 'connecting';
    this.notifyStatusChange();

    const url = `${WS_BASE_URL}${endpoint}`;
    console.log(`Connecting to Matrix: ${url}`);

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('Connected to the Matrix');
      this.status = 'connected';
      this.reconnectAttempts = 0;
      this.notifyStatusChange();
      this.startPingInterval();
    };

    this.ws.onclose = (event) => {
      console.log('Disconnected from the Matrix', event.code, event.reason);
      this.status = 'disconnected';
      this.notifyStatusChange();
      this.stopPingInterval();
      
      // Attempt reconnection
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
        setTimeout(() => this.connect(endpoint), this.reconnectDelay * this.reconnectAttempts);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.status = 'error';
      this.notifyStatusChange();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect(): void {
    this.stopPingInterval();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnected');
      this.ws = null;
    }
    
    this.status = 'disconnected';
    this.notifyStatusChange();
  }

  /**
   * Subscribe to WebSocket messages.
   */
  subscribe(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.handlers.delete(handler);
    };
  }

  /**
   * Send a message to the server.
   */
  send(type: string, data?: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('Cannot send message - not connected');
      return;
    }

    const message = {
      type,
      data,
      timestamp: new Date().toISOString(),
    };

    this.ws.send(JSON.stringify(message));
  }

  /**
   * Request current state from server.
   */
  requestState(): void {
    this.send('get_state');
  }

  /**
   * Request recent logs from server.
   */
  requestLogs(count: number = 50): void {
    this.send('get_logs', { count });
  }

  /**
   * Request current grid state.
   */
  requestGrid(): void {
    this.send('get_grid');
  }

  /**
   * Get current connection status.
   */
  getStatus(): ConnectionStatus {
    return this.status;
  }

  /**
   * Check if connected.
   */
  isConnected(): boolean {
    return this.status === 'connected';
  }

  private handleMessage(message: WSMessage): void {
    this.handlers.forEach(handler => {
      try {
        handler(message);
      } catch (e) {
        console.error('Error in message handler:', e);
      }
    });
  }

  private notifyStatusChange(): void {
    const statusMessage: WSMessage = {
      type: 'error', // Reusing error type for status
      timestamp: new Date().toISOString(),
      data: { status: this.status },
    };
    this.handleMessage(statusMessage);
  }

  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      this.send('ping');
    }, 30000); // Ping every 30 seconds
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
}

// Export singleton instance
export const matrixWS = new MatrixWebSocket();
