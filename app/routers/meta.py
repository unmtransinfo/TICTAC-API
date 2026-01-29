# app/routers/meta.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import handle_database_error
from app.db.database import get_db


router = APIRouter(prefix="/meta", tags=["meta"])


# /meta/health endpoint
@router.get(
    "/health",
    summary="Health check (service up)",
    description="Health check (service up)",
)
def health():
    return {"status": "ok"}


# /meta/counts endpoint
@router.get(
    "/counts",
    summary="High-level dataset counts (sanity + UX)",
    description="Counts for diseases, targets, drugs, studies, publications, evidence rows, and materialized views",
)
def counts(db: Session = Depends(get_db)):
    try:
        # counts
        disease_count = db.execute(
            text("SELECT COUNT(*) FROM core.disease")
        ).scalar_one()
        target_count = db.execute(text("SELECT COUNT(*) FROM core.target")).scalar_one()
        drug_count = db.execute(text("SELECT COUNT(*) FROM core.drug")).scalar_one()
        study_count = db.execute(text("SELECT COUNT(*) FROM core.study")).scalar_one()
        publication_count = db.execute(
            text("SELECT COUNT(*) FROM core.publication")
        ).scalar_one()

        # evidence rows. desciption for that table is: core evidence backbone in the docs
        evidence_count = db.execute(
            text("SELECT COUNT(*) FROM core.disease_target_study_drug")
        ).scalar_one()

        # mv (i think its correct becasue its showing 3. \dm core.*  )
        mv_count = db.execute(
            text("SELECT COUNT(*) FROM pg_matviews WHERE schemaname = 'core'")
        ).scalar_one()

        return {
            "diseases": disease_count,
            "targets": target_count,
            "drugs": drug_count,
            "studies": study_count,
            "publications": publication_count,
            "evidence_rows": evidence_count,
            "materialized_views": mv_count,
        }
    except Exception as e:
        raise handle_database_error(e, "counts")
