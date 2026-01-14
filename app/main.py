from fastapi import FastAPI

from app.routers import associations, diseases, meta, publications, studies

app = FastAPI(
    title="TICTAC API",
    description="Initial development version of the TICTAC backend.",
    version="0.1.0",
)

# Include routers with /api/v1 prefix
app.include_router(meta.router, prefix="/api/v1")
app.include_router(associations.router, prefix="/api/v1")
app.include_router(studies.router, prefix="/api/v1")
app.include_router(publications.router, prefix="/api/v1")
app.include_router(diseases.router, prefix="/api/v1")
