import os

from fastapi import FastAPI

# Check if we're running behind a reverse proxy
root_path = "/tictac" if os.getenv("BEHIND_PROXY") == "true" else ""

from app.routers import (
    associations,
    diseases,
    drugs,
    meta,
    publications,
    studies,
    targets,
)

app = FastAPI(
    title="TICTAC API",
    description="Initial development version of the TICTAC backend.",
    version="0.1.0",
    root_path=root_path,
)

# Include routers with /api/v1 prefix
app.include_router(meta.router, prefix="/api/v1")
app.include_router(associations.router, prefix="/api/v1")
app.include_router(studies.router, prefix="/api/v1")
app.include_router(publications.router, prefix="/api/v1")
app.include_router(diseases.router, prefix="/api/v1")
app.include_router(targets.router, prefix="/api/v1")
app.include_router(drugs.router, prefix="/api/v1")
