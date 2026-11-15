"""SBP API bootstrap. Device-control routes remain deliberately disabled."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.db import ping_database

app = FastAPI(
    title="Smart Battery Protector API",
    version="0.1.1",
    description="Development service scaffold; no device control endpoints are enabled.",
)

class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str

@app.get("/health/live", response_model=HealthResponse, tags=["operations"])
def liveness() -> HealthResponse:
    return HealthResponse(status="ok", service="sbp-api",
                          environment=os.getenv("SBP_ENV", "development"))

@app.get("/health/ready", response_model=HealthResponse, tags=["operations"])
def readiness() -> HealthResponse:
    if not ping_database():
        raise HTTPException(status_code=503, detail="database_not_ready")
    return HealthResponse(status="ok", service="sbp-api",
                          environment=os.getenv("SBP_ENV", "development"))
