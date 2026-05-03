"""
Configuration settings for the Matrix Simulation Backend.
Uses Pydantic Settings for environment variable management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore',  # Ignore extra env vars like frontend configs
    )
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./matrix_sim.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    # Logging
    log_level: str = "INFO"
    
    # Simulation
    simulation_tick_rate: float = 1.0  # seconds between ticks
    max_agents: int = 100
    grid_size: int = 20  # 20x20 grid
    
    # Energy collection
    base_energy_drain: float = 0.5  # energy drained per agent per tick
    conscious_energy_multiplier: float = 2.0  # conscious agents produce more
    
    # WebSocket
    ws_heartbeat_interval: float = 30.0


settings = Settings()
