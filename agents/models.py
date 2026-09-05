"""
Pydantic v2 schemas and data definitions for Lipid Nanoparticle Mrna Agent.
Domain: AI Drug Discovery, Structural Biology & Wet-Lab Robotics
Standard: wwPDB / IUPAC / OpenSMILES / ISAC Standards
"""
import datetime
import math
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


def _validate_finite_float(v: float, field_name: str) -> float:
    """Reject NaN, Infinity, and -Infinity values."""
    if not isinstance(v, (int, float)):
        raise ValueError(f"{field_name} must be a number")
    if math.isnan(v) or math.isinf(v):
        raise ValueError(f"{field_name} must be a finite number, got {v}")
    return float(v)


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier")
    target_identifier: str = Field(..., description="Entity, patient key, or genomic/cryptographic target")
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor")
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("primary_metric")
    @classmethod
    def validate_primary_metric(cls, v):
        return _validate_finite_float(v, "primary_metric")

    @field_validator("secondary_metric")
    @classmethod
    def validate_secondary_metric(cls, v):
        return _validate_finite_float(v, "secondary_metric")

    @field_validator("task_id", "target_identifier", "status_descriptor")
    @classmethod
    def validate_non_empty_string(cls, v):
        if not v or not str(v).strip():
            raise ValueError("Field cannot be empty or whitespace")
        return str(v).strip()


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "wwPDB / IUPAC / OpenSMILES / ISAC Standards"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "lipid-nanoparticle-mrna-agent"
    domain: str = "AI Drug Discovery, Structural Biology & Wet-Lab Robotics"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "wwPDB / IUPAC / OpenSMILES / ISAC Standards"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
