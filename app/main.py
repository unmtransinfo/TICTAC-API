from fastapi import FastAPI

from app.routers import (
    analytics,
    demo,
    disease,
    drug,
    evidence,
    ontology,
    target,
    trial,

    #New endpoints
    meta,
    associations,
    studies,
    publications,
    diseases,

)

app = FastAPI(
    title="TICTAC API",
    description="Initial development version of the TICTAC backend.",
    version="0.1.0",
)

# Include routers with /api/v1 prefix
'''
app.include_router(demo.router, prefix="/api/v1")
app.include_router(disease.router, prefix="/api/v1")
app.include_router(target.router, prefix="/api/v1")
app.include_router(evidence.router, prefix="/api/v1")
app.include_router(drug.router, prefix="/api/v1")
app.include_router(trial.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(ontology.router, prefix="/api/v1")
'''
app.include_router(meta.router, prefix="/api/v1")
app.include_router(associations.router, prefix="/api/v1")
app.include_router(studies.router, prefix="/api/v1")
app.include_router(publications.router, prefix="/api/v1")
app.include_router(diseases.router, prefix="/api/v1")
