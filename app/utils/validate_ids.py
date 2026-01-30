import re
from fastapi import HTTPException

# must start with DOID: followed by digits only
DOID_RE = re.compile(r"^DOID:\d+$")
# digits only
PMID_RE = re.compile(r"^\d+$")
# NCT + 8 digits
NCT_RE = re.compile(r"^NCT\d{8}$")

# UNIPROT_RE


def norm(s: str) -> str:
    return s.strip()


def validate_doid(doid: str) -> str:
    v = norm(doid).upper()
    if not DOID_RE.match(v):
        raise HTTPException(400, "Invalid DOID format")
    return v


def validate_nct(nct_id: str) -> str:
    v = nct_id.strip().upper()
    if not NCT_RE.match(v):
        raise HTTPException(400, "Invalid NCT ID format")
    return v


def validate_pmid(pmid: str) -> str:
    v = norm(pmid)
    if not PMID_RE.match(v):
        raise HTTPException(400, "Invalid PMID format")
    return v
