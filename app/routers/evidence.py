from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/evidence", tags=["evidence"])


class Publication(BaseModel):
    """Response model for publication provenance."""

    pmid: str
    title: str | None = None
    evidence_type: str | None = None


@router.get(
    "/get_provenance",
    response_model=List[Publication],
    summary="Get provenance for gene-disease pair",
    description="Retrieve provenance information (publications) for a specific gene–disease pair, including PMID, title, and evidence type.",
    responses={
        200: {
            "description": "List of publications with provenance information",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "pmid": "12345678",
                            "title": "BRCA1 mutations in breast cancer",
                            "evidence_type": "genetic_association",
                        },
                        {
                            "pmid": "87654321",
                            "title": "Role of BRCA1 in DNA repair",
                            "evidence_type": "functional_study",
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

