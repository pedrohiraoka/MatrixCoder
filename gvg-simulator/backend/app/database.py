"""
SQLAlchemy database setup for GvG Simulator
Only logs and transactions are persisted. Game state is in-memory.
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from typing import Optional
import os

DATABASE_URL = "sqlite+aiosqlite:///./gvg_simulator.db"

# Sync engine for SQLite
SYNC_DATABASE_URL = "sqlite:///./gvg_simulator.db"

engine = create_engine(SYNC_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class EventLog(Base):
    """Persisted event log"""
    __tablename__ = "event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    player_id = Column(String, ForeignKey("players.player_id"), nullable=True)


class Player(Base):
    """Player persistence (optional, for stats history)"""
    __tablename__ = "players"
    
    player_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    guild_id = Column(String, ForeignKey("guilds.guild_id"), nullable=True)
    total_ouro_earned = Column(Integer, default=0)
    total_ouro_spent = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Guild(Base):
    """Guild persistence (optional, for stats history)"""
    __tablename__ = "guilds"
    
    guild_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    leader_id = Column(String, nullable=False)
    total_ouro = Column(Integer, default=0)
    total_pontos_conquista = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    """Financial transaction log"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.player_id"), nullable=False)
    guild_id = Column(String, ForeignKey("guilds.guild_id"), nullable=True)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False)  # earn, spend, transfer
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def log_event_to_db(event_type: str, message: str, data: Optional[dict] = None, player_id: Optional[str] = None):
    """Log event to database"""
    db = SessionLocal()
    try:
        import json
        event = EventLog(
            event_type=event_type,
            message=message,
            data=json.dumps(data) if data else None,
            player_id=player_id
        )
        db.add(event)
        db.commit()
    finally:
        db.close()


def log_transaction(player_id: str, amount: int, transaction_type: str, 
                   description: Optional[str] = None, guild_id: Optional[str] = None):
    """Log financial transaction"""
    db = SessionLocal()
    try:
        transaction = Transaction(
            player_id=player_id,
            guild_id=guild_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description
        )
        db.add(transaction)
        
        # Update player stats
        player = db.query(Player).filter(Player.player_id == player_id).first()
        if player:
            if transaction_type == "earn":
                player.total_ouro_earned += amount
            elif transaction_type == "spend":
                player.total_ouro_spent += amount
        
        db.commit()
    finally:
        db.close()
