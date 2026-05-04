"""Configuração da aplicação via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação Matrix Simulator."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./matrix_sim.db"

    # Simulação
    simulation_tick_ms: int = 500
    ws_broadcast_interval: int = 100
    grid_size: int = 10

    # CORS
    cors_origins: str = "http://localhost:3000,ws://localhost:3000"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_cors_origins(self) -> List[str]:
        """Retorna lista de origens CORS."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
