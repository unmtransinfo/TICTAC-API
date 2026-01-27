# app/routers/associations.py
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import handle_database_error
from app.db.database import get_db

router = APIRouter(prefix="/associations", tags=["associations"])


# /associations/summary endpoint
@router.get(
    "/summary",
    summary="Ranked disease-target summary rows (main discovery surface)",
    description=(
        "Paginated list of disease-target pairs with metrics. "
        "Optional filters: doid, gene_symbol, uniprot, idgtdl, min_score, limit, offset."
    ),
)
def associations_summary(
    # important: doid input is following: e.g. DOID:1799
    doid: Optional[str] = None,
    gene_symbol: Optional[str] = None,
    uniprot: Optional[str] = None,
    # idgtdl
    idgtdl: Optional[str] = Query(default=None, description="Tclin/Tchem/Tbio/Tdark"),
    min_score: Optional[float] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    core.mv_disease_target_summary_plus
    """

    where = []
    params: Dict[str, Any] = {"limit": limit, "offset": offset}

    # checking if there is any input given and put them in sql query
    if doid:
        where.append("doid = :doid")
        params["doid"] = doid.strip()
    if gene_symbol:
        where.append("gene_symbol ILIKE :gene_symbol")
        params["gene_symbol"] = f"%{gene_symbol.strip()}%"
    if uniprot:
        where.append("uniprot = :uniprot")
        params["uniprot"] = uniprot.strip()
    if idgtdl:
        where.append("idgtdl = :idgtdl")
        params["idgtdl"] = idgtdl.strip()
    if min_score is not None:
        where.append("meanrankscore >= :min_score")
        params["min_score"] = float(min_score)

    # joining everything
    if len(where) > 0:
        where_sql = "WHERE " + " AND ".join(where)
    else:
        where_sql = ""

    # base_from
    base_from = f"""
        FROM core.mv_disease_target_summary_plus
        {where_sql}
    """

    try:
        # how many disase-target rows
        total = db.execute(text(f"SELECT COUNT(*) {base_from}"), params).scalar_one()

        # get the disease-target rows with their metrics
        rows = (
            db.execute(
                text(
                    f"""
                SELECT
                    doid,
                    disease_name,
                    gene_symbol,
                    uniprot,
                    idgtdl,


                    n_drugs,
                    n_studies,
                    n_publications,


                    meanrankscore,
                    meanrank,
                    percentile_meanrank
                {base_from}
                ORDER BY meanrankscore DESC NULLS LAST
                LIMIT :limit OFFSET :offset
                """
                ),
                params,
            )
            .mappings()
            .all()
        )

        return {
            "limit": limit,
            "offset": offset,
            "total": total,
            "items": list(rows),
        }
    except Exception as e:
        raise handle_database_error(e, "associations_summary")


# /associations/evidence endpoint
@router.get(
    "/evidence",
    summary="Evidence-level rows linking disease-target-drug-study (main provenance surface)",
    description="Paginated evidence rows including: DOID/name, UniProt/gene/TDL, drug (molecule_chembl_id, cid, drug_name), study (nct_id, title, phase, status, dates, enrollment, study_url)",
)
def associations_evidence(
    # disease_target did as written in the docs as doid_uniprot.
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
    """
    core.mv_tictac_associations
    """

    where = []
    params: Dict[str, Any] = {"limit": limit, "offset": offset}

    # e.g.disease_target="DOID:1799_P41597".
    # SELECT d.doid, t.uniprot_id FROM core.disease d JOIN core.disease_target dt ON dt.disease_id = d.disease_id JOIN core.target t ON t.target_id = dt.target_id WHERE d.doid = 'DOID:1799' LIMIT 5;
    if disease_target:
        s = disease_target.strip()
        if "_" in s:
            doid_val, uniprot_val = s.split("_", 1)
            where.append("doid = :doid_dt")
            where.append("uniprot = :uniprot_dt")
            params["doid_dt"] = doid_val
            params["uniprot_dt"] = uniprot_val

    # checking if there is any input given and put them in sql query
    if disease_name:
        where.append("disease_name ILIKE :disease_name")
        params["disease_name"] = f"%{disease_name.strip()}%"
    if gene_symbol:
        where.append("gene_symbol ILIKE :gene_symbol")
        params["gene_symbol"] = f"%{gene_symbol.strip()}%"
    if molecule_chembl_id:
        where.append("molecule_chembl_id = :chembl")
        params["chembl"] = molecule_chembl_id.strip()
    if nct_id:
        where.append("nct_id = :nct_id")
        params["nct_id"] = nct_id.strip()
    if phase:
        where.append("phase ILIKE :phase")
        params["phase"] = f"%{phase.strip()}%"
    if overall_status:
        where.append("UPPER(overall_status) = :overall_status")
        params["overall_status"] = overall_status.strip().upper()
    if exclude_withdrawn:
        # excluding. total statuses:  ACTIVE_NOT_RECRUITING,APPROVED_FOR_MARKETING,AVAILABLE, COMPLETED, ENROLLING_BY_INVITATION,NO_LONGER_AVAILABLE,NOT_YET_RECRUITING,RECRUITING,SUSPENDED,TEMPORARILY_NOT_AVAILABLE,TERMINATED,UNKNOWN,WITHDRAWN
        where.append("overall_status <> 'WITHDRAWN'")

    # joining everything
    if len(where) > 0:
        where_sql = "WHERE " + " AND ".join(where)
    else:
        where_sql = ""

    # base from
    base_from = f"""
        FROM core.mv_tictac_associations
        {where_sql}
    """

    try:
        # total
        total = db.execute(text(f"SELECT COUNT(*) {base_from}"), params).scalar_one()

        rows = (
            db.execute(
                text(
                    f"""
                SELECT
                    doid,
                    disease_name,
                    uniprot,
                    gene_symbol,
                    tcrdtargetname,
                    idgtdl,
                    nct_id,
                    official_title,
                    study_type,
                    phase,
                    overall_status,
                    start_date,
                    completion_date,
                    enrollment,
                    study_url,
                    cid,
                    molecule_chembl_id,
                    drug_name,
                    disease_target
                {base_from}
                ORDER BY doid, uniprot, molecule_chembl_id, nct_id
                LIMIT :limit OFFSET :offset
                """
                ),
                params,
            )
            .mappings()
            .all()
        )

        return {"limit": limit, "offset": offset, "total": total, "items": list(rows)}
    except Exception as e:
        raise handle_database_error(e, "associations_evidence")


# /associations/provenance_summary endpoint
@router.get(
    "/provenance_summary",
    summary="Disease-target pairs with trial evidence",
    description="Endpoint which shows disease-target pairs that have linked clinical trials (provenance)",
)
def provenance_summary(
    doid: str | None = None,
    gene_symbol: str | None = None,
    uniprot: str | None = None,
    idgtdl: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    core.mv_tictac_associations a
    """

    # threshold for provenance making it as disease-target that has at least 1 nct_id
    # using mv
    where = []
    params = {
        "doid": doid.strip() if doid else None,
        "gene_symbol": f"%{gene_symbol.strip()}%" if gene_symbol else None,
        "uniprot": uniprot.strip() if uniprot else None,
        "idgtdl": idgtdl.strip() if idgtdl else None,
        "limit": limit,
        "offset": offset,
    }

    where_sql = """
    WHERE (:doid IS NULL OR a.doid = :doid)
    AND (:gene_symbol IS NULL OR a.gene_symbol ILIKE :gene_symbol)
    AND (:uniprot IS NULL OR a.uniprot = :uniprot)
    AND (:idgtdl IS NULL OR a.idgtdl = :idgtdl)
    """

    try:
        # count how many unique disease target pairs exist
        total = db.execute(
            text(
                f"""
                SELECT COUNT(*) FROM (
                    SELECT a.doid, a.uniprot, a.gene_symbol, a.idgtdl
                    FROM core.mv_tictac_associations a

                    {where_sql}

                    GROUP BY a.doid, a.uniprot, a.gene_symbol, a.idgtdl
                ) x
            """
            ),
            params,
        ).scalar_one()

        # provenance
        rows = (
            db.execute(
                text(
                    f"""
                SELECT
                    a.doid,
                    a.disease_name,
                    a.uniprot,
                    a.gene_symbol,
                    a.idgtdl,

                    COUNT(DISTINCT a.nct_id) AS n_trials,
                    (COUNT(DISTINCT a.nct_id) > 0) AS has_provenance

                FROM core.mv_tictac_associations a

                {where_sql}

                GROUP BY a.doid, a.disease_name, a.uniprot, a.gene_symbol, a.idgtdl
                ORDER BY n_trials DESC
                LIMIT :limit OFFSET :offset
            """
                ),
                params,
            )
            .mappings()
            .all()
        )

        return {
            "limit": limit,
            "offset": offset,
            "total": total,
            "items": list(rows),
        }

    except Exception as e:
        raise handle_database_error(e, "provenance_summary")
