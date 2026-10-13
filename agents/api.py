"""
FastAPI REST API Server for Lipid Nanoparticle Mrna Agent.
"""
from typing import Dict, Any, List
from importlib.resources import files
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from lnp_formulator.calculations import np_ratio, encapsulation_efficiency_percent, protonated_fraction

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Lipid Nanoparticle Mrna Agent API",
    description="Enterprise Distributed Component Platform (AI Drug Discovery, Structural Biology & Wet-Lab Robotics)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


class MeasurementRequest(BaseModel):
    nitrogen_moles: float
    phosphate_moles: float
    total_mrna: float
    free_mrna: float
    ph: float
    pka: float


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def browser_interface():
    """Provide a same-origin UI so server audit requests work locally."""
    return files("web").joinpath("index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "lipid-nanoparticle-mrna-agent", "domain": "AI Drug Discovery, Structural Biology & Wet-Lab Robotics", "standard": "wwPDB / IUPAC / OpenSMILES / ISAC Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Sensitive identifier detected in request") from None
    return dossier.to_dict()


@app.post("/api/measure")
def api_measure(req: MeasurementRequest):
    try:
        return {
            "np_ratio": np_ratio(req.nitrogen_moles, req.phosphate_moles),
            "encapsulation_efficiency_percent": encapsulation_efficiency_percent(
                req.total_mrna, req.free_mrna
            ),
            "protonated_fraction_ideal": protonated_fraction(req.ph, req.pka),
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Sensitive identifier detected in request") from None


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
