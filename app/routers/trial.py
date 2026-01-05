from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/trial", tags=["trial"])


class ClinicalTrial(BaseModel):
    """Response model for clinical trial."""

    nct_id: str
    phase: str | None = None
    status: str | None = None


# TODO: add 200 response
@router.get(
    "/get_drug_trials",
    response_model=List[ClinicalTrial],
    summary="Get clinical trials for a drug",
    description="Retrieve all clinical trials mentioning a given drug, including NCT IDs, trial phases, and status.",
    responses={
        501: {
            "description": "Endpoint not implemented",
            "content": {"application/json": {"example": {"detail": "Not implemented"}}},
        },
    },
)
def get_drug_trials(drug_name: str):
    """
    Retrieve all clinical trials mentioning a given drug.

    Args:
        drug_name: Name of the drug to query.

    Returns:
        List of NCT IDs with trial phases and status.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
