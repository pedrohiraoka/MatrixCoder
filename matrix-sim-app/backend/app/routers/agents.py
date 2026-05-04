"""Roteadores para gerenciamento de agentes."""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models import Agente, AgenteEspecial
from app.services.agent_manager import AgentManager

router = APIRouter(prefix="/agents", tags=["Agentes"])


class CriarAgenteRequest(BaseModel):
    posicao_x: Optional[int] = Field(None, ge=0, le=9)
    posicao_y: Optional[int] = Field(None, ge=0, le=9)
    energia: float = Field(100.0, ge=0.0, le=200.0)


@router.get("", response_model=List[Agente])
async def listar_agentes():
    """Lista todos os agentes ativos na simulação."""
    manager = AgentManager.get_instance()
    return await manager.listar_agentes()


@router.post("", response_model=Agente, status_code=201)
async def criar_agente(request: CriarAgenteRequest):
    """
    Cria um novo agente na simulação.
    
    O agente será colocado em uma posição disponível se não especificada.
    """
    manager = AgentManager.get_instance()
    
    try:
        agente = await manager.adicionar_agente(
            posicao_x=request.posicao_x,
            posicao_y=request.posicao_y,
            energia=request.energia,
        )
        return agente
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{agente_id}", response_model=Agente)
async def obter_agente(agente_id: str):
    """Obtém detalhes de um agente específico."""
    manager = AgentManager.get_instance()
    agente = await manager.obter_agente(agente_id)
    
    if not agente:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    return agente


@router.patch("/{agente_id}/awaken", response_model=Agente)
async def despertar_agente(agente_id: str):
    """
    Desperta um agente, tornando-o consciente.
    
    Agentes conscientes podem ver o código da Matrix e manipular a simulação.
    Este é o equivalente a tomar a pílula vermelha.
    """
    manager = AgentManager.get_instance()
    agente = await manager.despertar_agente(agente_id)
    
    if not agente:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    return agente


@router.delete("/{agente_id}", status_code=204)
async def remover_agente(agente_id: str):
    """Remove um agente da simulação."""
    manager = AgentManager.get_instance()
    removido = await manager.remover_agente(agente_id)
    
    if not removido:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    return None


@router.post("/{agente_id}/move", response_model=Agente)
async def mover_agente(
    agente_id: str,
    posicao_x: int = Body(..., ge=0, le=9),
    posicao_y: int = Body(..., ge=0, le=9),
):
    """Move um agente para uma nova posição no grid."""
    manager = AgentManager.get_instance()
    
    agente = await manager.obter_agente(agente_id)
    if not agente:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    sucesso = await manager.mover_agente(agente_id, posicao_x, posicao_y)
    
    if not sucesso:
        raise HTTPException(
            status_code=400, detail="Posição inválida ou ocupada"
        )
    
    return await manager.obter_agente(agente_id)


@router.post("/{agente_id}/code", response_model=dict)
async def agente_ver_codigo(agente_id: str):
    """
    Permite que um agente consciente veja o código da Matrix.
    
    Apenas agentes com consciente=True podem usar este endpoint.
    """
    manager = AgentManager.get_instance()
    resultado = await manager.ver_codigo(agente_id)
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    if "erro" in resultado:
        raise HTTPException(status_code=403, detail=resultado["erro"])
    
    return resultado


@router.post("/{agente_id}/manipulate", response_model=dict)
async def agente_manipular_simulacao(
    agente_id: str,
    acao: str = Body(...),
    params: dict = Body(default_factory=dict),
):
    """
    Permite que um agente consciente manipule a simulação.
    
    Ações disponíveis:
    - injetar_energia: {"valor": float}
    - alterar_regra: {"chave": str, "valor": any}
    - resetar_metricas: {}
    """
    manager = AgentManager.get_instance()
    resultado = await manager.manipular_simulacao(agente_id, acao, params)
    
    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["mensagem"])
    
    return resultado
