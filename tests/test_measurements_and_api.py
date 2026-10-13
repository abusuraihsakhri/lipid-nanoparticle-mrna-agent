"""Regression checks for deterministic LNP calculations and API behavior."""
import json
import math

import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail
from lnp_formulator.calculations import (
    np_ratio, encapsulation_efficiency_percent, protonated_fraction, cumulants_pdi,
)
from lnp_formulator.cli import main as lnp_cli


def test_scientific_reference_examples():
    assert np_ratio(60, 10) == pytest.approx(6)
    assert np_ratio(0, 10) == pytest.approx(0)
    assert encapsulation_efficiency_percent(100, 8) == pytest.approx(92)
    assert encapsulation_efficiency_percent(100, 0) == pytest.approx(100)
    assert protonated_fraction(6.8, 6.8) == pytest.approx(0.5)
    assert protonated_fraction(5.8, 6.8) == pytest.approx(10 / 11)
    assert cumulants_pdi(10, 5) == pytest.approx(0.05)


@pytest.mark.parametrize("func,args", [
    (np_ratio, (10, 0)),
    (np_ratio, (-1, 4)),
    (np_ratio, (float("nan"), 4)),
    (np_ratio, (True, 4)),
    (encapsulation_efficiency_percent, (100, 101)),
    (encapsulation_efficiency_percent, (0, 0)),
    (encapsulation_efficiency_percent, (1, -1)),
    (protonated_fraction, (float("inf"), 6.8)),
    (cumulants_pdi, (0, 5)),
    (cumulants_pdi, (3, -1)),
])
def test_invalid_measurements_rejected(func, args):
    with pytest.raises(ValueError):
        func(*args)


def test_protonation_numerical_extremes():
    assert protonated_fraction(-100, 7) == 1
    assert protonated_fraction(100, 7) == 0


def test_cli_measurement(capsys):
    status = lnp_cli(["measure", "--nitrogen", "60", "--phosphate", "10",
                      "--total-mrna", "100", "--free-mrna", "8",
                      "--ph", "6.8", "--pka", "6.8"])
    assert status == 0
    values = json.loads(capsys.readouterr().out)
    assert values["np_ratio"] == pytest.approx(6)
    assert values["encapsulation_efficiency_percent"] == pytest.approx(92)
    assert values["protonated_fraction_ideal"] == pytest.approx(0.5)


def test_cli_rejects_invalid_measurement(capsys):
    assert lnp_cli(["measure", "--nitrogen", "1", "--phosphate", "0",
                    "--total-mrna", "2", "--free-mrna", "1",
                    "--ph", "7", "--pka", "7"]) == 2


def test_api_measure_and_browser():
    client = TestClient(app)
    response = client.post("/api/measure", json={
        "nitrogen_moles": 60, "phosphate_moles": 10, "total_mrna": 100,
        "free_mrna": 8, "ph": 6.8, "pka": 6.8,
    })
    assert response.status_code == 200
    assert response.json()["np_ratio"] == pytest.approx(6)
    assert client.get("/").status_code == 200
    assert "Measurement inputs" in client.get("/").text
    assert client.get("/health").status_code == 200


def test_api_rejects_invalid_values_and_sensitive_identifiers():
    client = TestClient(app)
    response = client.post("/api/measure", json={
        "nitrogen_moles": 10, "phosphate_moles": 0, "total_mrna": 100,
        "free_mrna": 8, "ph": 6.8, "pka": 6.8,
    })
    assert response.status_code == 422
    response = client.post("/api/audit", json={
        "task_id": "Patient MRN-1234567", "target_identifier": "SAMPLE-1",
        "primary_metric": 10,
    })
    assert response.status_code == 422
    assert "MRN-1234567" not in response.text


def test_audit_detects_content_tampering_without_chain_break():
    trail = AuditTrail(secret_key="known-test-key")
    trail.log("reviewer", "supervisor", "REVIEW", {"status": "OK"})
    trail.logs[0]["actor"] = "impostor"
    assert trail.verify_integrity() is False


def test_audit_log_snapshot_is_immutable_from_callers():
    trail = AuditTrail(secret_key="known-test-key")
    trail.log("reviewer", "supervisor", "REVIEW", {"status": "OK"})
    copy = trail.get_trail()
    copy[0]["actor"] = "impostor"
    assert trail.verify_integrity() is True


def test_unsupported_llm_provider_fails_explicitly():
    from agents.llm_factory import LLMFactory
    with pytest.raises(ValueError, match="Only mock inference"):
        LLMFactory.create("openai")
