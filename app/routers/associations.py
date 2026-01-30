# app/routers/associations.py
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import handle_database_error
from app.db.database import get_db

from app.utils.validate_query import validate_query_params

router = APIRouter(prefix="/associations", tags=["associations"])


# /associations/summary endpoint
@router.get(
    "/summary",
    summary="Ranked disease-target summary rows (main discovery surface)",
    description=(
        "Paginated list of disease-target pairs with metrics. "
        "Optional filters: doid, gene_symbol, uniprot, idgtdl, min_score, limit, offset."
    ),
    dependencies=[
        Depends(
            validate_query_params(
                {
                    "doid",
                    "gene_symbol",
                    "uniprot",
                    "idgtdl",
                    "min_score",
                    "limit",
                    "offset",
                }
            )
        )
    ],
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
            "items": list(rows),
        }
    except Exception as e:
        raise handle_database_error(e, "associations_summary")


# /associations/evidence endpoint
@router.get(
    "/evidence",
    summary="Evidence-level rows linking disease-target-drug-study (main provenance surface)",
    description="Paginated evidence rows including: DOID/name, UniProt/gene/TDL, drug (molecule_chembl_id, cid, drug_name), study (nct_id, title, phase, status, dates, enrollment, study_url)",
    dependencies=[
        Depends(
            validate_query_params(
                {
                    "doid",
                    "uniprot",
                    "disease_name",
                    "gene_symbol",
                    "molecule_chembl_id",
                    "nct_id",
                    "phase",
                    "overall_status",
                    "exclude_withdrawn",
                    "limit",
                    "offset",
                }
            )
        )
    ],
)
def associations_evidence(
    # Disease target in the docs but using doid and uniprot
    doid: str | None = None,
    uniprot: str | None = None,
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

    # disease target split into doid and uniprot
    if doid:
        where.append("doid = :doid")
        params["doid"] = doid.strip()

    if uniprot:
        where.append("uniprot = :uniprot")
        params["uniprot"] = uniprot.strip()

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

        return {"limit": limit, "offset": offset, "items": list(rows)}
    except Exception as e:
        raise handle_database_error(e, "associations_evidence")


# /associations/provenance_summary endpoint
@router.get(
    "/provenance_summary",
    summary="Disease-target pairs with trial evidence and publication",
    description="Endpoint which shows disease-target pairs that have linked clinical trials and publication (provenance)",
    dependencies=[
        Depends(
            validate_query_params(
                {
                    "doid",
                    "gene_symbol",
                    "uniprot",
                    "nct_id",
                    "pmid",
                    "limit",
                    "offset",
                }
            )
        )
    ],
)
def provenance_summary(
    doid: str | None = None,
    gene_symbol: str | None = None,
    uniprot: str | None = None,
    nct_id: str | None = None,
    pmid: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    core.mv_tictac_associations_summary s
    """

    # will match exact disease_target pair if both doid and uniprot given
    # otherwise will try to match on the prefix (if doid given), suffix (if uniprot given), or nothing (if neither given)
    disease_target_exact = None
    disease_target_prefix = None
    disease_target_suffix = None

    if doid and uniprot:
        disease_target_exact = f"{doid.strip()}_{uniprot.strip()}"
    elif doid:
        disease_target_prefix = f"{doid.strip()}_%"
    elif uniprot:
        disease_target_suffix = f"%_{uniprot.strip()}"

    params: Dict[str, Any] = {
        "disease_target_exact": disease_target_exact,
        "disease_target_prefix": disease_target_prefix,
        "disease_target_suffix": disease_target_suffix,
        "gene_symbol": f"%{gene_symbol.strip()}%" if gene_symbol else None,
        "nct_id": nct_id.strip() if nct_id else None,
        "pmid": pmid.strip() if pmid else None,
        "limit": limit,
        "offset": offset,
    }

    where_sql = """
    WHERE (:disease_target_exact IS NULL OR s.disease_target = :disease_target_exact)
      AND (:disease_target_prefix IS NULL OR s.disease_target LIKE :disease_target_prefix)
      AND (:disease_target_suffix IS NULL OR s.disease_target LIKE :disease_target_suffix)
      AND (:gene_symbol   IS NULL OR s.gene_symbol ILIKE :gene_symbol)
      AND (:nct_id        IS NULL OR s.nct_id = :nct_id)
      AND (:pmid          IS NULL OR s.pmid = :pmid)
    """

    try:
        # provenance
        rows = (
            db.execute(
                text(
                    f"""
                SELECT
                    s.disease_target,
                    s.gene_symbol,
                    s.nct_id,
                    s.pmid,
                    s.citation,
                    s.pubmed_url
                FROM core.mv_tictac_associations_summary s
                {where_sql}
                ORDER BY s.disease_target, s.gene_symbol, s.nct_id, s.pmid NULLS LAST
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
            "items": list(rows),
        }

    except Exception as e:
        raise handle_database_error(e, "provenance_summary")
