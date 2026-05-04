'use client';

import React, { useState, useRef, useEffect } from 'react';
import { despertarAgente, agenteVerCodigo, agenteManipular } from '@/lib/api';
import { Agente } from '@/lib/matrix_types';

interface ConsoleTerminalProps {
  agenteSelecionado: Agente | null;
  onComandoExecutado?: (resultado: any) => void;
}

interface HistoricoComando {
  comando: string;
  saida: any;
  timestamp: string;
}

export default function ConsoleTerminal({
  agenteSelecionado,
  onComandoExecutado,
}: ConsoleTerminalProps) {
  const [input, setInput] = useState('');
  const [historico, setHistorico] = useState<HistoricoComando[]>([]);
  const [historicoIndex, setHistoricoIndex] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const outputRef = useRef<HTMLDivElement>(null);

  const comandosDisponiveis = [
    'help',
    'clear',
    'ver_codigo',
    'manipular_simulacao',
    'status',
    'criar_agente',
    'despertar',
  ];

  const executarComando = async (comandoStr: string) => {
    const partes = comandoStr.trim().split(' ');
    const comando = partes[0].toLowerCase();
    const args = partes.slice(1).join(' ');

    let resultado: any;

    try {
      switch (comando) {
        case 'help':
          resultado = {
            ajuda: 'Comandos disponíveis:',
            comandos: comandosDisponiveis.map((c) => `  - ${c}`),
            exemplos: [
              '  ver_codigo',
              '  manipular_simulacao {"acao": "injetar_energia", "valor": 100}',
              '  criar_agente',
              '  despertar',
            ],
          };
          break;

        case 'clear':
          setHistorico([]);
          return;

        case 'ver_codigo':
          if (!agenteSelecionado) {
            resultado = { erro: 'Nenhum agente selecionado' };
          } else if (!agenteSelecionado.consciente) {
            resultado = {
              erro: 'Apenas agentes conscientes podem ver o código',
            };
          } else {
            resultado = await agenteVerCodigo(agenteSelecionado.id);
          }
          break;

        case 'manipular_simulacao':
          if (!agenteSelecionado) {
            resultado = { erro: 'Nenhum agente selecionado' };
          } else if (!agenteSelecionado.consciente) {
            resultado = {
              erro: 'Apenas agentes conscientes podem manipular a simulação',
            };
          } else {
            try {
              const params = JSON.parse(args || '{}');
              resultado = await agenteManipular(
                agenteSelecionado.id,
                params.acao || 'injetar_energia',
                params
              );
            } catch (e) {
              resultado = {
                erro: 'Formato inválido. Use: manipular_simulacao {"acao": "...", ...}',
              };
            }
          }
          break;

        case 'status':
          if (agenteSelecionado) {
            resultado = {
              agente: {
                id: agenteSelecionado.id,
                energia: agenteSelecionado.energia,
                consciente: agenteSelecionado.consciente,
                posicao: [agenteSelecionado.posicao_x, agenteSelecionado.posicao_y],
              },
            };
          } else {
            resultado = { mensagem: 'Nenhum agente selecionado' };
          }
          break;

        case 'criar_agente':
          resultado = {
            mensagem: 'Use o botão "Criar Agente" no dashboard',
          };
          break;

        case 'despertar':
          if (!agenteSelecionado) {
            resultado = { erro: 'Nenhum agente selecionado' };
          } else if (agenteSelecionado.consciente) {
            resultado = { mensagem: 'Agente já está desperto' };
          } else {
            await despertarAgente(agenteSelecionado.id);
            resultado = { sucesso: true, mensagem: 'Agente despertado!' };
          }
          break;

        default:
          resultado = {
            erro: `Comando desconhecido: ${comando}. Digite 'help' para ajuda.`,
          };
      }
    } catch (error: any) {
      resultado = { erro: error.message || 'Erro ao executar comando' };
    }

    const novoHistorico: HistoricoComando = {
      comando: comandoStr,
      saida: resultado,
      timestamp: new Date().toISOString(),
    };

    setHistorico((prev) => [...prev, novoHistorico]);
    onComandoExecutado?.(resultado);

    // Auto-scroll
    setTimeout(() => {
      if (outputRef.current) {
        outputRef.current.scrollTop = outputRef.current.scrollHeight;
      }
    }, 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (input.trim()) {
        executarComando(input);
        setInput('');
        setHistoricoIndex(null);
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historico.length > 0) {
        const newIndex = historicoIndex === null
          ? historico.length - 1
          : Math.max(0, historicoIndex - 1);
        setHistoricoIndex(newIndex);
        setInput(historico[newIndex].comando);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historicoIndex !== null) {
        const newIndex = historicoIndex + 1;
        if (newIndex >= historico.length) {
          setHistoricoIndex(null);
          setInput('');
        } else {
          setHistoricoIndex(newIndex);
          setInput(historico[newIndex].comando);
        }
      }
    }
  };

  const formatarSaida = (saida: any): string => {
    if (typeof saida === 'string') return saida;
    return JSON.stringify(saida, null, 2);
  };

  return (
    <div className="bg-matrix-bg-secondary border border-matrix-green rounded p-3 font-mono text-sm h-full flex flex-col">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-neon">CONSOLE</h3>
        <span className="text-xs text-matrix-dim">
          {agenteSelecionado
            ? `Agente: ${agenteSelecionado.id.slice(0, 8)}...`
            : 'Nenhum agente'}
        </span>
      </div>

      <div
        ref={outputRef}
        className="flex-1 overflow-y-auto mb-2 space-y-2 text-xs"
      >
        {historico.length === 0 ? (
          <div className="text-matrix-dim italic">
            Digite 'help' para ver comandos disponíveis...
          </div>
        ) : (
          historico.map((item, index) => (
            <div key={index} className="space-y-1">
              <div className="text-matrix-green">
                <span className="text-matrix-dim">{'> '}</span>
                {item.comando}
              </div>
              <div
                className={`${
                  item.saida.erro ? 'text-red-500' : 'text-matrix-dim'
                } whitespace-pre-wrap`}
              >
                {formatarSaida(item.saida)}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="flex items-center gap-2">
        <span className="text-neon">{'> '}</span>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="terminal-input flex-1"
          placeholder={
            agenteSelecionado?.consciente
              ? 'Digite um comando...'
              : 'Desperte um agente primeiro...'
          }
          disabled={!agenteSelecionado?.consciente && input.trim() !== ''}
          autoComplete="off"
        />
      </div>
    </div>
  );
}
