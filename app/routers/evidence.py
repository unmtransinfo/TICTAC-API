from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/evidence", tags=["evidence"])


class Publication(BaseModel):
    """Response model for publication provenance."""

    pmid: str
    title: str | None = None
    evidence_type: str | None = None


# TODO: add 200 response
@router.get(
    "/get_provenance",
    response_model=List[Publication],
    summary="Get provenance for gene-disease pair",
    description="Retrieve provenance information (publications) for a specific gene–disease pair, including PMID, title, and evidence type.",
    responses={
        501: {
            "description": "Endpoint not implemented",
            "content": {"application/json": {"example": {"detail": "Not implemented"}}},
        },
    },
)
def get_provenance(gene_symbol: str, disease_name: str):
    """
    Retrieve provenance info for a specific gene–disease pair.

    Args:
        gene_symbol: Gene symbol to query.
        disease_name: Disease name to query.

    Returns:
        List of publications with PMID, title, and evidence type.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
