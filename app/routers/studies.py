# app/routers/studies.py
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import handle_database_error
from app.db.database import get_db

from app.utils.validate_query import validate_query_params


router = APIRouter(prefix="/studies", tags=["studies"])


# /studies/search endpoint
@router.get(
    "/search",
    summary="Typeahead / lookup for studies",
    description="Typeahead / lookup for studies",
    dependencies=[Depends(validate_query_params({"q", "limit"}))],
)
def search_studies(
    q: str = Query(..., description="NCT or title substring"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        rows = (
            db.execute(
                text(
                    """
                SELECT

                    nct_id,
                    official_title,
                    overall_status,
                    phase,
                    study_url

                FROM core.study
                WHERE nct_id ILIKE :q
                   OR official_title ILIKE :q
                ORDER BY nct_id
                LIMIT :limit
                """
                ),
                {"q": f"%{q.strip()}%", "limit": limit},
            )
            .mappings()
            .all()
        )

        return list(rows)
    except Exception as e:
        raise handle_database_error(e, "search_studies")


# /studies/{nct_id} endpoint
@router.get(
    "/{nct_id}",
    summary="Fetch a single study's metadata + ClinicalTrials.gov link-out",
    description="Fetch a single study's metadata + ClinicalTrials.gov link-out",
    dependencies=[Depends(validate_query_params(set()))],
)
def get_study(nct_id: str, db: Session = Depends(get_db)):
    # e.g. NCT00137111, NCT00635258, NCT00340262, NCT01501019, NCT03912506

    # sanitize. regex with NCT+8digit
    nct_id = nct_id.strip().upper()

    if not re.match(r"^NCT\d{8}$", nct_id):
        raise HTTPException(status_code=400, detail="Invalid NCT-ID format.")

    try:
        row = (
            db.execute(
                text(
                    """
                SELECT
                    nct_id,

                    study_title AS title,
                    official_title,
                    phase,
                    overall_status AS status,

                    start_date,
                    completion_date,
                    start_year,

                    enrollment,
                    clinicaltrials_url,
                    study_url,

                    study_type,
                    source

                FROM core.study
                WHERE nct_id = :nct_id
                """
                ),
                {"nct_id": nct_id.strip()},
            )
            .mappings()
            .first()
        )

        if not row:
            raise HTTPException(status_code=404, detail="Study not found.")

        out = dict(row)

        return out
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "get_study")


# /studies/{nct_id}/publications endpoint
@router.get(
    "/{nct_id}/publications",
    summary="Publications supporting a given study (NCT -> PMIDs)",
    description="Publications supporting a given study (NCT -> PMIDs)",
    dependencies=[Depends(validate_query_params(set()))],
)
def study_publications(nct_id: str, db: Session = Depends(get_db)):
    """
    core.study s
    core.study_publication sp
    core.publication p
    """
    # e.g. NCT00137111, NCT00635258, NCT00340262, NCT01501019, NCT03912506

    # sanitize. regex with NCT+8digit
    nct_id = nct_id.strip().upper()

    if not re.match(r"^NCT\d{8}$", nct_id):
        raise HTTPException(status_code=400, detail="Invalid NCT ID format.")

    try:
        study_exists = db.execute(
            text("SELECT 1 FROM core.study WHERE nct_id = :nct_id"), {"nct_id": nct_id}
        ).first()

        if not study_exists:
            raise HTTPException(status_code=404, detail="Study not found.")

        rows = (
            db.execute(
                text(
                    """
                SELECT
                
                    p.pmid,
                    p.citation,
                    p.pubmed_url

                FROM core.study s
                JOIN core.study_publication sp ON sp.study_id = s.study_id
                JOIN core.publication p ON p.publication_id = sp.publication_id
                WHERE s.nct_id = :nct_id
                ORDER BY p.pmid
                """
                ),
                {"nct_id": nct_id.strip()},
            )
            .mappings()
            .all()
        )

        return list(rows)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "study_publications")
