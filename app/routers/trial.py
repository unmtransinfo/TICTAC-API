from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/trial", tags=["trial"])


class ClinicalTrial(BaseModel):
    """Response model for clinical trial."""

    nct_id: str
    phase: str | None = None
    status: str | None = None


@router.get(
    "/get_drug_trials",
    response_model=List[ClinicalTrial],
    summary="Get clinical trials for a drug",
    description="Retrieve all clinical trials mentioning a given drug, including NCT IDs, trial phases, and status.",
    responses={
        200: {
            "description": "List of clinical trials",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "nct_id": "NCT12345678",
                            "phase": "Phase 3",
                            "status": "Completed",
                        },
                        {
                            "nct_id": "NCT87654321",
                            "phase": "Phase 2",
                            "status": "Recruiting",
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
def get_drug_trials(drug_name: str):
    """
    Retrieve all clinical trials mentioning a given drug.

    Args:
        drug_name: Name of the drug to query.

    Returns:
        List of NCT IDs with trial phases and status.
    """
    raise HTTPException(status_code=501, detail="Not implemented")

