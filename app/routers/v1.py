from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db, test_connection
from app.models.study import Study

router = APIRouter(prefix="/api/v1", tags=["v1"])


class ConnectionResponse(BaseModel):
    """Response model for connection test."""

    connected: bool
    message: str


class StudyResponse(BaseModel):
    """Response model for study data."""

    study_id: int
    nct_id: str

    class Config:
        from_attributes = True


@router.get(
    "/can_connect",
    summary="Test database connection",
    description="Verifies that the API can successfully connect to the PostgreSQL database.",
    responses={
        200: {
            "description": "Connection test completed",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful connection",
                            "value": {
                                "connected": True,
                                "message": "Successfully connected to the database",
                            },
                        },
                        "failure": {
                            "summary": "Failed connection",
                            "value": {
                                "connected": False,
                                "message": "Failed to connect to the database",
                            },
                        },
                    }
                }
            },
        }
    },
)
def can_connect():
    is_connected = test_connection()

    if is_connected:
        return ConnectionResponse(
            connected=True, message="Successfully connected to the database"
        )
    else:
        return ConnectionResponse(
            connected=False, message="Failed to connect to the database"
        )


@router.get(
    "/get_study",
    response_model=StudyResponse,
    summary="Get study by ID",
    description="Retrieves a single study from the core.study table using the study_id.",
    responses={
        200: {
            "description": "Study found and returned successfully",
            "content": {
                "application/json": {
                    "example": {"study_id": 1, "nct_id": "NCT12345678"}
                }
            },
        },
        404: {
            "description": "Study not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Study with study_id 1 not found"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error retrieving study: <error message>"}
                }
            },
        },
    },
)
def get_study(study_id: int, db: Session = Depends(get_db)):
    try:
        study = db.query(Study).filter(Study.study_id == study_id).first()
        if study is None:
            raise HTTPException(
                status_code=404, detail=f"Study with study_id {study_id} not found"
            )
        return study
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving study: {str(e)}")
