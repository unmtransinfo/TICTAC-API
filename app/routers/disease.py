from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
def get_associated_targets(disease_name: str):
    """
    Retrieve all targets associated with a given disease.

    Args:
        disease_name: Name of the disease to query.

    Returns:
        List of gene symbols with evidence metrics.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
