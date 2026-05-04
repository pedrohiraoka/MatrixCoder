"""Roteadores para operações de simulação."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.models import MatrixState, ComandoConsole, RespostaManipulacao
from app.services.agent_manager import AgentManager

router = APIRouter(prefix="/simulation", tags=["Simulação"])


@router.get("/state", response_model=MatrixState)
async def obter_estado_simulacao():
    """
    Obtém o estado atual da simulação.
    
    Retorna o grid, métricas e contadores atuais.
    """
    manager = AgentManager.get_instance()
    return manager.matrix.obter_estado()


@router.post("/tick")
async def forcar_tick():
    """
    Força a execução de um tick manual da simulação.
    
    Útil para debugging ou controle passo-a-passo.
    """
    manager = AgentManager.get_instance()
    
    # Executa um tick manualmente
    await manager.manager._executar_tick() if hasattr(manager, 'manager') else None
    
    return {
        "mensagem": "Tick executado",
        "estado": manager.matrix.obter_estado().dict(),
    }


@router.get("/code")
async def ver_codigo_matrix():
    """
    Revela o código interno da Matrix.
    
    Endpoint especial que mostra as regras, estado bruto e logs.
    Inspirado no conceito de "ver o código" da Matrix.
    """
    manager = AgentManager.get_instance()
    codigo = manager.matrix.ver_codigo()
    
    return {
        "sucesso": True,
        "dados": codigo,
        "mensagem": "Você viu além da simulação.",
    }


@router.post("/manipulate", response_model=RespostaManipulacao)
async def manipular_simulacao(acao: str, params: Dict[str, Any] = None):
    """
    Manipula parâmetros da simulação.
    
    Requer um agente consciente (implementação simplificada para admin).
    """
    manager = AgentManager.get_instance()
    
    if params is None:
        params = {}
    
    resultado = manager.matrix.manipular_simulacao(acao, params)
    
    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["mensagem"])
    
    return RespostaManipulacao(**resultado)
