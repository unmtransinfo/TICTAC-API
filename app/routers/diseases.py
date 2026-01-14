#app/routers/diseases.py
from typing import List, Optional, Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from fastapi import Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db



router = APIRouter(prefix="/diseases", tags=["diseases"])





#/diseases/search
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
    '''
    core.disease d
    '''

    #IMPORTANT: so just assuming for this one we are doing searches both disease name OR DOID because docs doesnt specify how to lookup


    #e.g. DOID:17
    rows = db.execute(
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
    ).mappings().all()

    return list(rows)


