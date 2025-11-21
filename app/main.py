from fastapi import FastAPI

app = FastAPI(
    title="TICTAC API",
    description="Initial development version of the TICTAC backend.",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "TICTAC API - Initial Development Phase"}
