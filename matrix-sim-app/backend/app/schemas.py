# Pydantic Schemas for API Request/Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ML Schemas
class MLSimulationRequest(BaseModel):
    n_samples: int = Field(default=1000, ge=100, le=10000)
    contamination: float = Field(default=0.1, ge=0.01, le=0.5)
    n_features: int = Field(default=5, ge=2, le=20)


class MLSimulationResponse(BaseModel):
    total_samples: int
    anomalies_detected: int
    anomaly_percentage: float
    model_score: float
    processing_time_ms: float
    summary_stats: Dict[str, Any]


# Data Processing Schemas
class DataProcessRequest(BaseModel):
    data: List[Dict[str, Any]]
    transformations: List[str] = Field(default=["normalize", "aggregate"])


class DataProcessResponse(BaseModel):
    rows_processed: int
    columns: List[str]
    metrics: Dict[str, Any]
    preview: List[Dict[str, Any]]


# Crypto Schemas
class CryptoEncryptRequest(BaseModel):
    payload: str = Field(..., min_length=1)
    key_name: Optional[str] = "default"


class CryptoDecryptRequest(BaseModel):
    encrypted_data: str
    key_name: Optional[str] = "default"


class CryptoResponse(BaseModel):
    result: str
    algorithm: str = "Fernet"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Log Schema
class LogEntry(BaseModel):
    timestamp: datetime
    module: str
    action: str
    details: Dict[str, Any]
    status: str
