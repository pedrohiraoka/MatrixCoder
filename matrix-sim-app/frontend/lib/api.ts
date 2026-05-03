/**
 * API client for Matrix Simulation backend.
 * Handles REST API calls with proper error handling.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

import { Agent, GridState, MatrixState, SimulationStatus, LogEntry } from './matrix_types';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// ============== Simulation Endpoints ==============

export async function getSimulationStatus(): Promise<SimulationStatus> {
  const response = await fetch(`${API_BASE_URL}/simulation/status`);
  return handleResponse<SimulationStatus>(response);
}

export async function controlSimulation(action: 'start' | 'stop' | 'reset'): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/simulation/control`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  });
  return handleResponse(response);
}

export async function getMatrixState(): Promise<MatrixState> {
  const response = await fetch(`${API_BASE_URL}/simulation/state`);
  return handleResponse<MatrixState>(response);
}

export async function getGridState(): Promise<GridState> {
  const response = await fetch(`${API_BASE_URL}/simulation/grid`);
  return handleResponse<GridState>(response);
}

export async function spawnAgents(count: number = 5): Promise<{ agents: Agent[] }> {
  const response = await fetch(`${API_BASE_URL}/simulation/spawn-agents?count=${count}`, {
    method: 'POST',
  });
  return handleResponse(response);
}

// ============== Agent Endpoints ==============

export async function getAgents(): Promise<Agent[]> {
  const response = await fetch(`${API_BASE_URL}/agents/`);
  return handleResponse<Agent[]>(response);
}

export async function getAgent(agentId: string): Promise<Agent> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}`);
  return handleResponse<Agent>(response);
}

export async function createAgent(
  position_x: number,
  position_y: number,
  name?: string,
  is_conscious: boolean = false
): Promise<{ agent: Agent }> {
  const response = await fetch(`${API_BASE_URL}/agents/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ position_x, position_y, name, is_conscious }),
  });
  return handleResponse(response);
}

export async function deleteAgent(agentId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
}

export async function awakenAgent(agentId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}/awaken`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agent_id: agentId, red_pill: true }),
  });
  return handleResponse(response);
}

export async function putAgentToSleep(agentId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}/sleep`, {
    method: 'POST',
  });
  return handleResponse(response);
}

export async function viewAgentCode(agentId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}/view-code`, {
    method: 'POST',
  });
  return handleResponse(response);
}

export async function manipulateSimulation(
  agentId: string,
  manipulation_type: 'teleport' | 'energy_boost' | 'rule_override',
  target_x?: number,
  target_y?: number,
  value?: number
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/agents/${agentId}/manipulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent_id: agentId,
      manipulation_type,
      target_x,
      target_y,
      value,
    }),
  });
  return handleResponse(response);
}

export async function getAgentStatistics(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/agents/statistics`);
  return handleResponse(response);
}

export async function getConsciousAgents(): Promise<{ count: number; agents: Agent[] }> {
  const response = await fetch(`${API_BASE_URL}/agents/conscious/list`);
  return handleResponse(response);
}

// ============== Admin Endpoints ==============

export async function getHealth(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse(response);
}

export async function getSystemLogs(count: number = 100): Promise<{ logs: LogEntry[] }> {
  const response = await fetch(`${API_BASE_URL}/admin/logs?count=${count}`);
  return handleResponse(response);
}

export async function resetSystem(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/admin/reset`, {
    method: 'POST',
  });
  return handleResponse(response);
}
