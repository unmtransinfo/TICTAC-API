# app/routers/diseases.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import handle_database_error
from app.db.database import get_db

router = APIRouter(prefix="/diseases", tags=["diseases"])


# /diseases/search
@router.get(
    "/search",
    summary="Typeahead / lookup for diseases",
    description="Typeahead / lookup for diseases",
)
def search_diseases(
    q: str = Query(..., description="Substring search"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    core.disease d
    """

    # IMPORTANT: so just assuming for this one we are doing searches both disease name OR DOID because docs doesnt specify how to lookup

    # e.g. DOID:17
    try:
        rows = (
            db.execute(
                text(
                    """
                SELECT
                    d.doid,
                    d.preferred_name AS disease_name

                FROM core.disease d
                WHERE d.preferred_name ILIKE :q
                   OR d.doid ILIKE :q

                ORDER BY d.preferred_name
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
        raise handle_database_error(e, "search_diseases")
