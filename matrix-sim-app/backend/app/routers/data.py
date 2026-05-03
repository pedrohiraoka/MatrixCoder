# Data Router - Data Processing and Transformation
from fastapi import APIRouter, HTTPException
from app.schemas import DataProcessRequest, DataProcessResponse
from app.services.data_processor import data_processor
from app.database import get_session
from app.models import SimulationLog
from datetime import datetime

router = APIRouter(prefix="/api/data", tags=["Data Processing"])


@router.post("/process", response_model=DataProcessResponse)
async def process_data(request: DataProcessRequest):
    """
    Process and transform data using Pandas.
    Supports normalization, aggregation, rolling means, and log transforms.
    """
    try:
        # Load data
        data_processor.load_data(request.data)

        # Apply transformations
        metrics = data_processor.apply_transformations(request.transformations)

        # Get preview and columns
        preview = data_processor.get_preview(5)
        columns = data_processor.get_columns()

        # Log to database
        session = next(get_session())
        log_entry = SimulationLog(
            module="data",
            action="process_data",
            details={
                "rows": len(request.data),
                "transformations": request.transformations,
            },
            status="success",
        )
        session.add(log_entry)
        session.commit()

        return DataProcessResponse(
            rows_processed=len(request.data),
            columns=columns,
            metrics=metrics,
            preview=preview,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data processing failed: {str(e)}")


@router.get("/stats")
async def get_stats():
    """Get statistics about processed data"""
    if data_processor.df is None:
        return {"message": "No data loaded"}

    stats = {
        "rows": len(data_processor.df),
        "columns": len(data_processor.df.columns),
        "column_names": data_processor.get_columns(),
        "dtypes": data_processor.df.dtypes.astype(str).to_dict(),
        "null_counts": data_processor.df.isnull().sum().to_dict(),
    }
    return stats
