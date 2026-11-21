"""SBP API bootstrap. Device-control routes remain deliberately disabled."""
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.account import router as account_router
from app.db import ping_database
from app.device_data import router as device_data_router
from app.device_events import router as device_router
from app.telemetry import router as telemetry_router

app = FastAPI(
    title="Smart Battery Protector API",
    version="0.7.0",
    description="Development API; Ed25519-authenticated device event and telemetry ingestion, user device binding, status and history are enabled; power control is not.",
)

app.include_router(device_router)
app.include_router(account_router)
app.include_router(telemetry_router)
app.include_router(device_data_router)


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
