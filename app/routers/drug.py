from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/drug", tags=["drug"])


class DrugTarget(BaseModel):
    """Response model for drug target with bioactivity."""

    target_name: str
    bioactivity_summary: str | None = None
    # Add other bioactivity metrics as needed


@router.get(
    "/get_associated_targets",
    response_model=List[DrugTarget],
    summary="Get targets associated with a drug",
    description="Get targets or scaffolds linked to a drug via aact_drugs_chembl_activity, including bioactivity summaries.",
    responses={
        200: {
            "description": "List of targets with bioactivity summaries",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "target_name": "EGFR",
                            "bioactivity_summary": "IC50: 10nM",
                        },
                        {
                            "target_name": "HER2",
                            "bioactivity_summary": "IC50: 25nM",
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
def get_associated_targets(drug_name: str):
    """
    Get targets or scaffolds linked to a drug.

    Args:
        drug_name: Name of the drug to query.

    Returns:
        List of targets with bioactivity summaries.
    """
    raise HTTPException(status_code=501, detail="Not implemented")

