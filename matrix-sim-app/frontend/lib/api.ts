/**
 * Wrappers tipados para chamadas à API REST do backend.
 */

import { Agente, MatrixState, LogEntry, CriarAgenteRequest, RespostaManipulacao } from './matrix_types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BACKEND_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
    throw new Error(error.detail || `Erro HTTP ${response.status}`);
  }

  return response.json();
}

// Agentes
export async function getAgentes(): Promise<Agente[]> {
  return fetchAPI<Agente[]>('/agents');
}

export async function getAgente(id: string): Promise<Agente> {
  return fetchAPI<Agente>(`/agents/${id}`);
}

export async function criarAgente(data: CriarAgenteRequest): Promise<Agente> {
  return fetchAPI<Agente>('/agents', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function despertarAgente(id: string): Promise<Agente> {
  return fetchAPI<Agente>(`/agents/${id}/awaken`, {
    method: 'PATCH',
  });
}

export async function removerAgente(id: string): Promise<void> {
  await fetchAPI<void>(`/agents/${id}`, {
    method: 'DELETE',
  });
}

export async function moverAgente(id: string, x: number, y: number): Promise<Agente> {
  return fetchAPI<Agente>(`/agents/${id}/move`, {
    method: 'POST',
    body: JSON.stringify({ posicao_x: x, posicao_y: y }),
  });
}

export async function agenteVerCodigo(id: string): Promise<any> {
  return fetchAPI<any>(`/agents/${id}/code`, {
    method: 'POST',
  });
}

export async function agenteManipular(
  id: string,
  acao: string,
  params?: Record<string, any>
): Promise<RespostaManipulacao> {
  return fetchAPI<RespostaManipulacao>(`/agents/${id}/manipulate`, {
    method: 'POST',
    body: JSON.stringify({ acao, params }),
  });
}

// Simulação
export async function getSimulationState(): Promise<MatrixState> {
  return fetchAPI<MatrixState>('/simulation/state');
}

export async function verCodigoMatrix(): Promise<any> {
  return fetchAPI<any>('/simulation/code');
}

export async function manipularSimulacao(
  acao: string,
  params?: Record<string, any>
): Promise<RespostaManipulacao> {
  return fetchAPI<RespostaManipulacao>(
    `/simulation/manipulate?acao=${encodeURIComponent(acao)}`,
    {
      method: 'POST',
      body: JSON.stringify(params || {}),
    }
  );
}

// Admin
export async function resetarSimulacao(): Promise<any> {
  return fetchAPI<any>('/admin/reset', {
    method: 'POST',
  });
}

export async function iniciarSimulacao(): Promise<any> {
  return fetchAPI<any>('/admin/start', {
    method: 'POST',
  });
}

export async function pararSimulacao(): Promise<any> {
  return fetchAPI<any>('/admin/stop', {
    method: 'POST',
  });
}

export async function getStatus(): Promise<any> {
  return fetchAPI<any>('/admin/status');
}

export async function injetarAgenteEspecial(): Promise<any> {
  return fetchAPI<any>('/admin/inject-special-agent', {
    method: 'POST',
  });
}

export async function exportarLogs(): Promise<{ total: number; logs: LogEntry[] }> {
  return fetchAPI<{ total: number; logs: LogEntry[] }>('/admin/logs/export');
}

// Health check
export async function healthCheck(): Promise<any> {
  return fetchAPI<any>('/health');
}
