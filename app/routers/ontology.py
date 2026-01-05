from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/ontology", tags=["ontology"])


class OntologyMapping(BaseModel):
    """Response model for ontology mapping."""

    disease_name: str
    do_label: str | None = None
    umls_xref: str | None = None


# TODO: add 200 response
@router.get(
    "/get_umls_mapping",
    response_model=OntologyMapping,
    summary="Get UMLS mapping for a disease",
    description="Fetch ontology mapping for a disease, including Disease Ontology (DO) label and UMLS cross-reference.",
    responses={
        501: {
            "description": "Endpoint not implemented",
            "content": {"application/json": {"example": {"detail": "Not implemented"}}},
        },
    },
)
def get_umls_mapping(disease_name: str):
    """
    Fetch ontology mapping for a disease.

    Args:
        disease_name: Name of the disease to query.

    Returns:
        DO label and UMLS cross-reference.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
