from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/ontology", tags=["ontology"])


class OntologyMapping(BaseModel):
    """Response model for ontology mapping."""

    disease_name: str
    do_label: str | None = None
    umls_xref: str | None = None


@router.get(
    "/get_umls_mapping",
    response_model=OntologyMapping,
    summary="Get UMLS mapping for a disease",
    description="Fetch ontology mapping for a disease, including Disease Ontology (DO) label and UMLS cross-reference.",
    responses={
        200: {
            "description": "Ontology mapping information",
            "content": {
                "application/json": {
                    "example": {
                        "disease_name": "Breast Cancer",
                        "do_label": "DOID:1612",
                        "umls_xref": "C0006142",
                    }
                }
            },
        },
        404: {
            "description": "Disease not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Disease not found in ontology"}
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
def get_umls_mapping(disease_name: str):
    """
    Fetch ontology mapping for a disease.

    Args:
        disease_name: Name of the disease to query.

    Returns:
        DO label and UMLS cross-reference.
    """
    raise HTTPException(status_code=501, detail="Not implemented")

