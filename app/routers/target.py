from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/target", tags=["target"])


class DiseaseEvidence(BaseModel):
    """Response model for disease with evidence scores."""

    disease_name: str
    evidence_score: float | None = None
    # Add other evidence metrics as needed


# TODO: add 200 response
@router.get(
    "/get_associated_diseases",
    response_model=List[DiseaseEvidence],
    summary="Get diseases associated with a target",
    description="Retrieve all diseases linked to a gene/target, including evidence scores.",
    responses={
        501: {
            "description": "Endpoint not implemented",
            "content": {"application/json": {"example": {"detail": "Not implemented"}}},
        },
    },
)
def get_associated_diseases(gene_symbol: str):
    """
    Retrieve all diseases linked to a gene/target.

    Args:
        gene_symbol: Gene symbol to query.

    Returns:
        List of diseases with evidence scores.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
