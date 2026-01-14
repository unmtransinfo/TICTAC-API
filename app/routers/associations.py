#app/routers/associations.py
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/associations", tags=["associations"])




#/associations/summary endpoint
@router.get(
    "/summary",
    summary="Ranked disease-target summary rows (main discovery surface)",
    description=(
        "Paginated list of disease-target pairs with metrics. "
        "Optional filters: doid, gene_symbol, uniprot, idgtdl, min_score, limit, offset."
    ),
)
def associations_summary(


    #important: doid input is following: e.g. DOID:1799
    doid: Optional[str] = None,

    gene_symbol: Optional[str] = None,
    uniprot: Optional[str] = None,
    #idgtdl
    idgtdl: Optional[str] = Query(default=None, description="Tclin/Tchem/Tbio/Tdark"),
    min_score: Optional[float] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    '''
    core.disease_target dt
    core.disease d 
    core.target t
    core.disease_target_metrics m
    '''



    where = []
    params: Dict[str, Any] = {"limit": limit, "offset": offset}


    #checking if there is any input given and put them in sql query
    if doid:
        where.append("d.doid = :doid")
        params["doid"] = doid.strip()
    if gene_symbol:
        where.append("t.gene_symbol ILIKE :gene_symbol")
        params["gene_symbol"] = gene_symbol.strip()
    if uniprot:
        where.append("t.uniprot_id = :uniprot")
        params["uniprot"] = uniprot.strip()
    if idgtdl:
        where.append("t.idg_tdl = :idgtdl")
        params["idgtdl"] = idgtdl.strip()
    if min_score is not None:
        where.append("m.meanrankscore >= :min_score")
        params["min_score"] = float(min_score)

 

    #joining everything
    if len(where) > 0:
        where_sql = "WHERE " + " AND ".join(where)
    else:
        where_sql = ""
   

    #joins the disease, target and metrics tables together and add input where_sql
    base_from = f"""
        FROM core.disease_target dt
        JOIN core.disease d ON d.disease_id = dt.disease_id
        JOIN core.target t ON t.target_id = dt.target_id
        LEFT JOIN core.disease_target_metrics m ON m.disease_target_id = dt.disease_target_id
        {where_sql}
    """

    #how many disase-target rows exist after we join(base_from)
    total = db.execute(text(f"SELECT COUNT(*) {base_from}"), params).scalar_one()


    #get the disease-target rows with their metrics from the joined tables, apply sortin and pagination
    rows = db.execute(
        text(
            f"""
            SELECT
                d.doid,
                d.preferred_name AS disease_name,
                t.gene_symbol,
                t.uniprot_id AS uniprot,
                t.idg_tdl AS idgtdl,


                m.ndrug AS n_drugs,
                m.nstud AS n_studies,
                m.npub  AS n_publications,


                m.meanrankscore,
                m.meanrank,
                m.percentile_meanrank
            {base_from}
            ORDER BY m.meanrankscore DESC NULLS LAST
            LIMIT :limit OFFSET :offset
            """
        ),
        params,
    ).mappings().all()


    return {
        "limit": limit,
        "offset": offset,
        "total": total,
        "items": list(rows),
    }
    



#/associations/evidence endpoint
@router.get(
    "/evidence",
    summary="Evidence-level rows linking disease-target-drug-study (main provenance surface)",
    description="Paginated evidence rows including: DOID/name, UniProt/gene/TDL, drug (molecule_chembl_id, cid, drug_name), study (nct_id, title, phase, status, dates, enrollment, study_url)",
)
def associations_evidence(

    #disease_target did as written in the docs as doid_uniprot.
    disease_target: Optional[str] = Query(default=None, description="DOID:..._UNIPROT"),
    disease_name: Optional[str] = Query(default=None, description="ILIKE filter"),
    gene_symbol: Optional[str] = None,
    molecule_chembl_id: Optional[str] = None,
    nct_id: Optional[str] = None,
    phase: Optional[str] = None,
    overall_status: Optional[str] = None,
    exclude_withdrawn: bool = False,
    limit: int = Query(default=100, ge=1, le=1000), 
    offset: int = Query(default=0, ge=0), 
    db: Session = Depends(get_db),
):
    '''
    core.disease_target_study_drug e
    core.disease_target dt
    core.disease d
    core.drug dr
    core.target t
    core.study s
    core.drug_name dn
    '''


    where = []
    params: Dict[str, Any] = {"limit": limit, "offset": offset}




    #e.g.disease_target="DOID:1799_P41597". 
    #SELECT d.doid, t.uniprot_id FROM core.disease d JOIN core.disease_target dt ON dt.disease_id = d.disease_id JOIN core.target t ON t.target_id = dt.target_id WHERE d.doid = 'DOID:1799' LIMIT 5;
    if disease_target:
        s = disease_target.strip()
        if "_" in s:
            doid_val, uniprot_val = s.split("_", 1)
            where.append("d.doid = :doid_dt")
            where.append("t.uniprot_id = :uniprot_dt")
            params["doid_dt"] = doid_val
            params["uniprot_dt"] = uniprot_val


    #checking if there is any input given and put them in sql query
    if disease_name:
        where.append("d.preferred_name ILIKE :disease_name")
        params["disease_name"] = f"%{disease_name.strip()}%"
    if gene_symbol:
        where.append("t.gene_symbol ILIKE :gene_symbol")
        params["gene_symbol"] = f"%{gene_symbol.strip()}%"
    if molecule_chembl_id:
        where.append("dr.molecule_chembl_id = :chembl")
        params["chembl"] = molecule_chembl_id.strip()
    if nct_id:
        where.append("s.nct_id = :nct_id")
        params["nct_id"] = nct_id.strip()
    if phase:
        where.append("s.phase ILIKE :phase")
        params["phase"] = f"%{phase.strip()}%"
    if overall_status:
        where.append("s.overall_status ILIKE :overall_status")
        params["overall_status"] = f"%{overall_status.strip()}%"
    if exclude_withdrawn:
        #excluding. total statuses:  ACTIVE_NOT_RECRUITING,APPROVED_FOR_MARKETING,AVAILABLE, COMPLETED, ENROLLING_BY_INVITATION,NO_LONGER_AVAILABLE,NOT_YET_RECRUITING,RECRUITING,SUSPENDED,TEMPORARILY_NOT_AVAILABLE,TERMINATED,UNKNOWN,WITHDRAWN
        where.append("s.overall_status <> 'WITHDRAWN'")


    #joining everything
    if len(where) > 0:
        where_sql = "WHERE " + " AND ".join(where)
    else:
        where_sql = ""



    ##join disease, target, drug and study table and select one drug name per drug(DESC makes true come first) and do where_sql
    base_from = f"""
        FROM core.disease_target_study_drug e
        JOIN core.disease_target dt ON dt.disease_target_id = e.disease_target_id
        JOIN core.disease d ON d.disease_id = dt.disease_id
        JOIN core.target t ON t.target_id = dt.target_id
        JOIN core.drug dr ON dr.drug_id = e.drug_id
        JOIN core.study s ON s.study_id = e.study_id


        LEFT JOIN LATERAL (
            SELECT dn.drug_name
            FROM core.drug_name dn
            WHERE dn.drug_id = dr.drug_id
            ORDER BY dn.is_preferred DESC, dn.drug_name ASC
            LIMIT 1
        ) dn ON TRUE



        {where_sql}
    """


    #total
    total = db.execute(text(f"SELECT COUNT(*) {base_from}"), params).scalar_one()




    rows = db.execute(
        text(
            f"""
            SELECT
                d.doid,
                d.preferred_name AS disease_name,

                t.uniprot_id,
                t.gene_symbol,
                t.idg_tdl,


                dr.molecule_chembl_id,
                dr.cid,
                dn.drug_name,


                s.nct_id,
                s.study_title AS title,
                s.phase,
                s.overall_status AS status,
                s.start_date,
                s.completion_date,
                s.enrollment,
                COALESCE(s.study_url, s.clinicaltrials_url) AS study_url,

                e.source
            {base_from}
            ORDER BY d.doid, t.uniprot_id, dr.molecule_chembl_id, s.nct_id
            LIMIT :limit OFFSET :offset
            """
        ),
        params,
    ).mappings().all()




    return {
        "limit": limit, 
        "offset": offset, 
        "total": total, 
        "items": list(rows)
    }

