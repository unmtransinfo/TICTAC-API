# app/routers/publications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import handle_database_error
from app.db.database import get_db

from app.utils.validate_query import validate_query_params
from app.utils.validate_ids import validate_pmid


router = APIRouter(prefix="/publications", tags=["publications"])


# /router/publications/{pmid} endpoint
@router.get(
    "/{pmid}",
    summary="Publication details + PubMed link-out",
    description="Publication details + PubMed link-out",
    dependencies=[Depends(validate_query_params(set()))],
)
def get_publication(pmid: str, db: Session = Depends(get_db)):
    """ """
    pmid = validate_pmid(pmid)

    # e.g.1000144, 1000466, 1000470, 100122

    try:
        row = (
            db.execute(
                text(
                    """
                SELECT

                    pmid,
                    citation,
                    pubmed_url

                FROM core.publication
                WHERE pmid = :pmid
                """
                ),
                {"pmid": pmid.strip()},
            )
            .mappings()
            .first()
        )

        if not row:
            raise HTTPException(status_code=404, detail="Publication not found.")

        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "get_publication")
