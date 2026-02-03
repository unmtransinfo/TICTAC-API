# app/routers/associations.py
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import handle_database_error
from app.db.database import get_db
from app.utils.validate_ids import validate_doid, validate_nct, validate_pmid
from app.utils.validate_query import validate_query_params

router = APIRouter(prefix="/associations", tags=["associations"])


def _join_where(where: list[str]) -> str:
    # joining everything
    where_sql = ""
    if len(where) > 0:
        where_sql = "WHERE " + " AND ".join(where)
    return where_sql


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

    # Validating the input query
    if doid:
        doid = validate_doid(doid)

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
    where_sql = _join_where(where)

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

    # Validating the input query
    if doid:
        doid = validate_doid(doid)
    if nct_id:
        nct_id = validate_nct(nct_id)

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
    where_sql = _join_where(where)

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

    # Validating the input query
    if doid:
        doid = validate_doid(doid)
    if nct_id:
        nct_id = validate_nct(nct_id)
    if pmid:
        pmid = validate_pmid(pmid)

    where = []
    params: Dict[str, Any] = {"limit": limit, "offset": offset}

    # checking if there is any input given and put them in sql query
    if doid:
        where.append("doid = :doid")
        params["doid"] = doid.strip()
    if uniprot:
        where.append("uniprot = :uniprot")
        params["uniprot"] = uniprot.strip()
    if gene_symbol:
        where.append("gene_symbol ILIKE :gene_symbol")
        params["gene_symbol"] = f"%{gene_symbol.strip()}%"
    if nct_id:
        where.append("nct_id = :nct_id")
        params["nct_id"] = nct_id.strip()
    if pmid:
        where.append("pmid = :pmid")
        params["pmid"] = pmid.strip()

    # joining everything
    where_sql = _join_where(where)

    try:
        # provenance
        rows = (
            db.execute(
                text(
                    f"""
                SELECT
                    doid,
                    uniprot,
                    gene_symbol,
                    nct_id,
                    pmid,
                    citation
                FROM core.mv_tictac_associations_summary
                {where_sql}
                ORDER BY doid, uniprot, gene_symbol, nct_id, pmid NULLS LAST
                LIMIT :limit OFFSET :offset
                """
                ),
                params,
            )
            .mappings()
            .all()
        )

        # Add computed fields for API consistency
        items = []
        for row in rows:
            item = dict(row)
            item["disease_target"] = f"{row['doid']}_{row['uniprot']}"
            item["pubmed_url"] = (
                f"https://pubmed.ncbi.nlm.nih.gov/{row['pmid']}/"
                if row["pmid"]
                else None
            )
            items.append(item)

        return {
            "limit": limit,
            "offset": offset,
            "items": items,
        }

    except Exception as e:
        raise handle_database_error(e, "provenance_summary")
