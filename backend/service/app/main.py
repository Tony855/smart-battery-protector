"""SBP API bootstrap. Device-control routes remain deliberately disabled."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.db import ping_database
from app.device_events import router as device_router
from app.account import router as account_router
from app.telemetry import router as telemetry_router

app = FastAPI(
    title="Smart Battery Protector API",
    version="0.4.0",
    description="Development API; authenticated device event ingestion and user device binding and authenticated telemetry are enabled; power control is not.",
)

app.include_router(device_router)
app.include_router(account_router)
app.include_router(telemetry_router)

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
