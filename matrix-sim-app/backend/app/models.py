"""Modelos Pydantic e SQLAlchemy para a aplicação Matrix."""

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from typing import Optional, Dict, Tuple, List, Any
from app.database import Base


# =============================================================================
# Modelos SQLAlchemy (Database)
# =============================================================================


class LogEntryDB(Base):
    """Modelo SQLAlchemy para logs da simulação."""

    __tablename__ = "log_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    nivel = Column(String(20), nullable=False, index=True)  # INFO, WARN, ERROR, AWAKEN
    mensagem = Column(Text, nullable=False)
    contexto = Column(Text, nullable=True)  # JSON string

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "nivel": self.nivel,
            "mensagem": self.mensagem,
            "contexto": self.contexto,
        }


# =============================================================================
# Modelos Pydantic (Schemas)
# =============================================================================


class AgenteBase(BaseModel):
    """Schema base para agente."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    posicao_x: int = Field(ge=0, le=9, default=0)
    posicao_y: int = Field(ge=0, le=9, default=0)
    energia: float = Field(ge=0.0, default=100.0)
    consciente: bool = False

    model_config = ConfigDict(from_attributes=True)


class Agente(AgenteBase):
    """Schema completo para agente comum."""

    regras_comportamento: Dict[str, Any] = Field(
        default_factory=lambda: {
            "prob_movimento": 0.7,
            "prob_interacao": 0.3,
            "limiar_energia": 20.0,
        }
    )

    @property
    def posicao(self) -> Tuple[int, int]:
        return (self.posicao_x, self.posicao_y)


class AgenteEspecial(Agente):
    """Schema para agente especial (desperto/consciente)."""

    consciente: bool = True
    permissoes: List[str] = Field(
        default_factory=lambda: ["ver_codigo", "manipular_simulacao"]
    )


class CeldaGrid(BaseModel):
    """Schema para uma célula do grid da Matrix."""

    ocupado: bool = False
    agente_id: Optional[str] = None
    energia_ambiental: float = Field(ge=0.0, default=50.0)


class MatrixState(BaseModel):
    """Estado completo da Matrix."""

    grid: List[List[CeldaGrid]] = Field(
        default_factory=lambda: [
            [CeldaGrid() for _ in range(10)] for _ in range(10)
        ]
    )
    tempo_simulacao: int = 0
    energia_total_coletada: float = 0.0
    agentes_despertos: int = 0
    ticks_executados: int = 0

    model_config = ConfigDict(from_attributes=True)


class LogEntry(BaseModel):
    """Schema para entrada de log."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    nivel: str  # INFO, WARN, ERROR, AWAKEN
    mensagem: str
    contexto: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class MensagemWS(BaseModel):
    """Schema para mensagens WebSocket."""

    type: str  # TICK, LOG, AGENTE_UPDATE, ERROR
    payload: Dict[str, Any]


class ComandoConsole(BaseModel):
    """Schema para comandos do console."""

    comando: str
    params: Optional[Dict[str, Any]] = None


class RespostaManipulacao(BaseModel):
    """Resposta de manipulação da simulação."""

    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
