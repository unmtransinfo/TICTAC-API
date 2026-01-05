from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/disease", tags=["disease"])


class TargetEvidence(BaseModel):
    """Response model for target with evidence metrics."""

    gene_symbol: str
    mean_rank: float | None = None
    n_pub: int | None = None
    # Add other evidence metrics as needed


@router.get(
    "/get_associated_targets",
    response_model=List[TargetEvidence],
    summary="Get targets associated with a disease",
    description="Retrieve all targets (genes) associated with a given disease, including evidence metrics such as MeanRank and nPub.",
    responses={
        200: {
            "description": "List of targets with evidence metrics",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "gene_symbol": "BRCA1",
                            "mean_rank": 1.5,
                            "n_pub": 150,
                        },
                        {
                            "gene_symbol": "TP53",
                            "mean_rank": 2.3,
                            "n_pub": 200,
                        },
                    ]
                }
            },
        },
        501: {
            "description": "Endpoint not implemented",
            "content": {
                "application/json": {"example": {"detail": "Not implemented"}}
            },
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

