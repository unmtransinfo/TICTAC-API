from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/drug", tags=["drug"])


class DrugTarget(BaseModel):
    """Response model for drug target with bioactivity."""

    target_name: str
    bioactivity_summary: str | None = None
    # Add other bioactivity metrics as needed


# TODO: add 200 response
@router.get(
    "/get_associated_targets",
    response_model=List[DrugTarget],
    summary="Get targets associated with a drug",
    description="Get targets or scaffolds linked to a drug via aact_drugs_chembl_activity, including bioactivity summaries.",
    responses={
        501: {
            "description": "Endpoint not implemented",
            "content": {"application/json": {"example": {"detail": "Not implemented"}}},
        },
    },
)
def get_associated_targets(drug_name: str):
    """
    Get targets or scaffolds linked to a drug.

    Args:
        drug_name: Name of the drug to query.

    Returns:
        List of targets with bioactivity summaries.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
