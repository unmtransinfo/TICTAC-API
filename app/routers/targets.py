# app/routers/targets.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.exceptions import handle_database_error
from app.db.database import get_db


router = APIRouter(prefix="/targets", tags=["targets"])


# /targets/search
@router.get(
    "/search",
    summary="Typeahead / lookup for targets",
    description="Typeahead / lookup for targets",
)
def search_targets(
    q: str = Query(..., description="Gene symbol or UniProt substring"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    core.target t
    """

    # q is a substring search used for uniprot_id or gene_symbol mentioned in docs
    # IMPORTANT: tcrdtargetname(Target Central Resource Database?) is core.target.protein_name in this

    # e.g. of gene_symbol: ZNF560
    try:
        rows = (
            db.execute(
                text(
                    """
                SELECT

                    t.uniprot_id AS uniprot,
                    t.gene_symbol,
                    t.idg_tdl AS idgtdl,

                    t.protein_name AS tcrdtargetname

                FROM core.target t
                WHERE t.uniprot_id ILIKE :q
                   OR t.gene_symbol ILIKE :q
                ORDER BY t.gene_symbol NULLS LAST
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
        raise handle_database_error(e, "search_targets")
