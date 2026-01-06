from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db

router = APIRouter(prefix="/disease", tags=["disease"])


class TargetEvidence(BaseModel):
    """Response model for target with evidence metrics."""

    gene_symbol: str
    mean_rank: float | None = None
    n_pub: int | None = None
    # Add other evidence metrics as needed


# TODO: add 200 response
@router.get(
    "/get_associated_targets",
    response_model=List[TargetEvidence],
    summary="Get targets associated with a disease",
    description="Retrieve all targets (genes) associated with a given disease, including evidence metrics such as MeanRank and nPub.",
    responses={
        501: {
            "description": "Endpoint not implemented",
            "content": {"application/json": {"example": {"detail": "Not implemented"}}},
        },
    },
)
def get_associated_targets(disease_name: str, db:Session=Depends(get_db)):
    """
    Retrieve all targets associated with a given disease.

    Args:
        disease_name: Name of the disease to query.

    Returns:
        List of gene symbols with evidence metrics.
    """
    result = db.execute(
        text("""
        SELECT gene_symbol,
               mean_rank_score AS mean_rank,
               n_publications::int AS n_pub

        FROM core.disease_target_association
        WHERE doid = :doid
        ORDER BY mean_rank_score NULLS LAST
        """),
        {"doid": disease_name},
    ).mappings().all()

    return result