#app/routers/associations.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/studies", tags=["studies"])





#/studies/{nct_id} endpoint
@router.get(
    "/{nct_id}",
    summary="Fetch a single study's metadata + ClinicalTrials.gov link-out",
    description="Fetch a single study's metadata + ClinicalTrials.gov link-out",
)
def get_study(nct_id: str, db: Session = Depends(get_db)):
    #e.g. NCT00137111, NCT00635258, NCT00340262, NCT01501019, NCT03912506

    
    row = db.execute(
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
    ).mappings().first()


    out = dict(row)


    return out



#/studies/{nct_id}/publications endpoint
@router.get(
    "/{nct_id}/publications",
    summary="Publications supporting a given study (NCT -> PMIDs)",
    description="Publications supporting a given study (NCT -> PMIDs)",
)
def study_publications(nct_id: str, db: Session = Depends(get_db)):
    '''
    core.study s
    core.study_publication sp
    core.publication p
    '''
    #e.g. NCT00137111, NCT00635258, NCT00340262, NCT01501019, NCT03912506


    rows = db.execute(
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
    ).mappings().all()

    

    return list(rows)

