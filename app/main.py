from fastapi import FastAPI

from app.routers import v1

app = FastAPI(
    title="TICTAC API",
    description="Initial development version of the TICTAC backend.",
    version="0.1.0",
)

# Include routers
app.include_router(v1.router)


@app.get("/")
def root():
    return {"message": "TICTAC API - Initial Development Phase"}
