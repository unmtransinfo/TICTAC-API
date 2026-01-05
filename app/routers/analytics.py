from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/analytics", tags=["analytics"])


class UnderstudiedTarget(BaseModel):
    """Response model for understudied target ranking."""

    gene_symbol: str
    rank: int
    mean_rank: float | None = None
    n_pub: int | None = None
    metric_value: float | None = None


@router.get(
    "/get_top_understudied_targets",
    response_model=List[UnderstudiedTarget],
    summary="Get top understudied targets for a disease",
    description='Rank "Tbio" genes by MeanRank or publication scarcity for a disease. Returns a ranked list of understudied targets.',
    responses={
        200: {
            "description": "Ranked list of understudied targets",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "gene_symbol": "GENE1",
                            "rank": 1,
                            "mean_rank": 1.2,
                            "n_pub": 5,
                            "metric_value": 0.95,
                        },
                        {
                            "gene_symbol": "GENE2",
                            "rank": 2,
                            "mean_rank": 1.8,
                            "n_pub": 8,
                            "metric_value": 0.87,
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
def get_top_understudied_targets(disease_name: str, metric: str | None = None):
    """
    Rank "Tbio" genes by MeanRank or publication scarcity for a disease.

    Args:
        disease_name: Name of the disease to query.
        metric: Optional metric to use for ranking (e.g., "mean_rank", "n_pub").

    Returns:
        Ranked JSON list of understudied targets.
    """
    raise HTTPException(status_code=501, detail="Not implemented")

