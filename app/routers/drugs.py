# app/routers/drugs.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.exceptions import handle_database_error
from app.db.database import get_db


router = APIRouter(prefix="/drugs", tags=["drugs"])


# drugs/search endpoint
@router.get(
    "/search",
    summary="Typeahead / lookup for drugs",
    description="Typeahead / lookup for drugs",
)
def search_drugs(
    q: str = Query(..., description="Drug name substring"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    core.drug d
    core.drug_name dn
    """

    try:
        rows = (
            db.execute(
                text(
                    """
                SELECT
                    d.molecule_chembl_id,
                    d.cid,
                    dn.drug_name
                FROM core.drug d
                JOIN core.drug_name dn ON dn.drug_id = d.drug_id
                WHERE dn.is_preferred = true
                  AND dn.drug_name ILIKE :q
                ORDER BY dn.drug_name
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
        raise handle_database_error(e, "search_drugs")
