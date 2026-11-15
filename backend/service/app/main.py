"""SBP API bootstrap. Only health endpoints are enabled until auth and DB are wired."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Smart Battery Protector API",
    version="0.1.0",
    description="Development scaffold; no device control endpoints are enabled.",
)

class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str

@app.get("/health/live", response_model=HealthResponse, tags=["operations"])
def liveness() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="sbp-api",
        environment=os.getenv("SBP_ENV", "development"),
    )

@app.get("/health/ready", response_model=HealthResponse, tags=["operations"])
def readiness() -> HealthResponse:
    # Readiness must remain unavailable until database, broker and auth checks exist.
    raise HTTPException(status_code=503, detail="dependencies_not_configured")
