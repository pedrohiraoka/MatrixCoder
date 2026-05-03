# SQLAlchemy/SQLModel Models
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class SimulationLog(SQLModel, table=True):
    __tablename__ = "simulation_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    module: str  # ml, data, crypto
    action: str
    details: dict = Field(sa_column_kwargs={"default": {}})
    anomaly_score: Optional[float] = None
    status: str = "success"


class CryptoKeyStore(SQLModel, table=True):
    __tablename__ = "crypto_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    key_name: str = Field(unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
