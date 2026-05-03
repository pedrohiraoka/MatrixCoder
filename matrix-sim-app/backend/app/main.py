# FastAPI Main Application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.database import create_db_and_tables
from app.routers import ml, data, crypto, ws

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("matrix-api")

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Matrix Simulation API - ML, Data Processing, and Cryptography",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ml.router)
app.include_router(data.router)
app.include_router(crypto.router)
app.include_router(ws.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Matrix Simulation API...")
    create_db_and_tables()
    logger.info("Database tables created")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Matrix Simulation API...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Matrix Simulation API",
        "version": settings.APP_VERSION,
        "endpoints": {
            "ml": "/api/ml/simulate",
            "data": "/api/data/process",
            "crypto_encrypt": "/api/crypto/encrypt",
            "crypto_decrypt": "/api/crypto/decrypt",
            "ws_logs": "/ws/logs",
            "ws_ml": "/ws/simulate",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "matrix-sim-api"}
