"""
Security and Input Validation Tests for Lipid Nanoparticle Mrna Agent.
Tests for PHI guard, input validation, and error handling improvements.
"""
import sys
import math
import os
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditTrail, AuditLogger, SecurityException
from agents.models import SystemTaskPayload, _validate_finite_float
from cli import main


class TestPHIGuard:
    """Test PHI detection and redaction."""

    def test_mrn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")

    def test_ssn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phone_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call patient at 555-123-4567")

    def test_email_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email patient at john@example.com")

    def test_dob_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1985")

    def test_patient_name_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name: John Smith")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("LNP formulation N/P ratio 6.5")

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 test")
        assert "REDACTED_IDENTIFIER" in result
        assert "MRN-12345678" not in result


class TestInputValidation:
    """Test input validation for metric values."""

    def test_nan_rejected(self):
        with pytest.raises(ValueError, match="finite number"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("nan")
            )

    def test_positive_infinity_rejected(self):
        with pytest.raises(ValueError, match="finite number"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("inf")
            )

    def test_negative_infinity_rejected(self):
        with pytest.raises(ValueError, match="finite number"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("-inf")
            )

    def test_secondary_nan_rejected(self):
        with pytest.raises(ValueError, match="finite number"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=10.0,
                secondary_metric=float("nan")
            )

    def test_valid_values_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=28.5,
            secondary_metric=14.2
        )
        assert payload.primary_metric == 28.5
        assert payload.secondary_metric == 14.2

    def test_zero_values_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=0.0,
            secondary_metric=0.0
        )
        assert payload.primary_metric == 0.0

    def test_negative_values_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=-5.0,
            secondary_metric=-2.0
        )
        assert payload.primary_metric == -5.0

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="",
                target_identifier="KEY-01",
                primary_metric=10.0
            )

    def test_whitespace_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="   ",
                target_identifier="KEY-01",
                primary_metric=10.0
            )

    def test_empty_target_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="",
                primary_metric=10.0
            )


class TestAuditTrailSecurity:
    """Test audit trail security improvements."""

    def test_ephemeral_key_generation(self):
        """When no key is provided, an ephemeral key should be generated."""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            trail = AuditTrail()
        assert len(trail.secret_key) > 0

    def test_explicit_key_used(self):
        """When a key is provided, it should be used."""
        trail = AuditTrail(secret_key="test-key-123")
        assert trail.secret_key == b"test-key-123"

    def test_env_var_key_used(self):
        """When AUDIT_SECRET_KEY env var is set, it should be used."""
        os.environ["AUDIT_SECRET_KEY"] = "env-key-456"
        try:
            trail = AuditTrail()
            assert trail.secret_key == b"env-key-456"
        finally:
            del os.environ["AUDIT_SECRET_KEY"]

    def test_audit_trail_integrity(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_B", {"data": "value2"})
        assert trail.verify_integrity() is True

    def test_audit_trail_tamper_detection(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_B", {"data": "value2"})
        # Tamper with the chain
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False


class TestBatchCLIErrorHandling:
    """Test batch CLI error handling."""

    def test_missing_input_file(self):
        result = main(["batch", "-i", "nonexistent_file.csv"])
        assert result == 1

    def test_batch_with_valid_csv(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n")
            f.write("TASK-001,TARGET-01,12.0,4.1,false,NOMINAL\n")
            f.write("TASK-002,TARGET-02,35.0,19.5,true,ANOMALY\n")
            temp_path = f.name

        output_path = temp_path.replace('.csv', '_output.csv')
        try:
            result = main(["batch", "-i", temp_path, "-o", output_path])
            assert result == 0
            assert os.path.exists(output_path)
        finally:
            os.unlink(temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_batch_with_malformed_csv(self):
        """Malformed rows are skipped, valid processing completes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write("task_id,target_identifier,primary_metric\n")
            f.write("TASK-001,TARGET-01,not_a_number\n")  # Invalid float - will be skipped
            temp_path = f.name

        output_path = temp_path.replace('.csv', '_output.csv')
        try:
            result = main(["batch", "-i", temp_path, "-o", output_path])
            assert result == 0  # Command succeeds, bad row is skipped
            assert os.path.exists(output_path)
        finally:
            os.unlink(temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
