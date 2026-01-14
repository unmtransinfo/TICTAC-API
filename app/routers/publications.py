#app/routers/publications.py
from typing import List, Optional, Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from fastapi import Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db


router = APIRouter(prefix="/publications", tags=["publications"])


#/router/publications/{pmid} endpoint
@router.get(
    "/{pmid}",
    summary="Publication details + PubMed link-out",
    description="Publication details + PubMed link-out",
)
def get_publication(pmid: str, db: Session = Depends(get_db)):
    '''
    '''

    #e.g.1000144, 1000466, 1000470, 100122

    row = db.execute(
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
    ).mappings().first()


    return dict(row)

