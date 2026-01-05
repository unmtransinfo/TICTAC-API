from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/target", tags=["target"])


class DiseaseEvidence(BaseModel):
    """Response model for disease with evidence scores."""

    disease_name: str
    evidence_score: float | None = None
    # Add other evidence metrics as needed


@router.get(
    "/get_associated_diseases",
    response_model=List[DiseaseEvidence],
    summary="Get diseases associated with a target",
    description="Retrieve all diseases linked to a gene/target, including evidence scores.",
    responses={
        200: {
            "description": "List of diseases with evidence scores",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "disease_name": "Breast Cancer",
                            "evidence_score": 0.95,
                        },
                        {
                            "disease_name": "Ovarian Cancer",
                            "evidence_score": 0.87,
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
def get_associated_diseases(gene_symbol: str):
    """
    Retrieve all diseases linked to a gene/target.

    Args:
        gene_symbol: Gene symbol to query.

    Returns:
        List of diseases with evidence scores.
    """
    raise HTTPException(status_code=501, detail="Not implemented")

