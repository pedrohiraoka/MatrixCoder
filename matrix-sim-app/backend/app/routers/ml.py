# ML Router - Simulation and Anomaly Detection
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.schemas import MLSimulationRequest, MLSimulationResponse
from app.services.ml_engine import ml_engine
from app.database import get_session
from app.models import SimulationLog
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.post("/simulate", response_model=MLSimulationResponse)
async def simulate_anomalies(request: MLSimulationRequest):
    """
    Generate synthetic data and detect anomalies using Isolation Forest.
    This simulates "glitches in the Matrix".
    """
    try:
        # Generate synthetic data
        df, true_labels = ml_engine.generate_synthetic_data(
            n_samples=request.n_samples,
            n_features=request.n_features,
            contamination=request.contamination,
        )

        # Detect anomalies
        results = ml_engine.detect_anomalies(df, request.contamination)

        # Log to database
        session = next(get_session())
        log_entry = SimulationLog(
            module="ml",
            action="simulate_anomalies",
            details={
                "n_samples": request.n_samples,
                "n_features": request.n_features,
            },
            anomaly_score=results["model_score"],
            status="success",
        )
        session.add(log_entry)
        session.commit()

        return MLSimulationResponse(**results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML simulation failed: {str(e)}")


@router.websocket("/ws/simulate")
async def websocket_simulate(websocket: WebSocket):
    """
    WebSocket endpoint for real-time ML simulation streaming.
    Continuously generates and analyzes data streams.
    """
    await websocket.accept()

    try:
        while True:
            # Receive config from client
            data = await websocket.receive_json()
            n_samples = data.get("n_samples", 500)
            n_features = data.get("n_features", 5)
            contamination = data.get("contamination", 0.1)

            # Run simulation
            df, _ = ml_engine.generate_synthetic_data(
                n_samples=n_samples,
                n_features=n_features,
                contamination=contamination,
            )
            results = ml_engine.detect_anomalies(df, contamination)

            # Send results
            await websocket.send_json(
                {
                    "type": "simulation_result",
                    "data": results,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Small delay to prevent overwhelming
            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print("Client disconnected from ML WebSocket")
    except Exception as e:
        await websocket.send_json({"type": "error", "detail": str(e)})
