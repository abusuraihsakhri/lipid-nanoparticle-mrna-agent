"""Regression tests for exported CSV and finite LNP values."""
import csv
import pytest
from cli import main as main_cli
from lnp_formulator.cli import main as lnp_cli
from lnp_formulator.models import FrontierPayload

@pytest.mark.parametrize("run", [main_cli, lnp_cli])
def test_csv_export(tmp_path, run):
    src = tmp_path / "input.csv"
    dest = tmp_path / "output.csv"
    src.write_text("task_id,target_identifier,primary_metric,secondary_metric,status_descriptor\n=1+1,SAMPLE-01,-5,1,NOMINAL\n")
    assert run(["batch", "-i", str(src), "-o", str(dest)]) == 0
    with dest.open(newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["task_id"] == "'=1+1"
    assert row["primary_metric"] == "-5"

@pytest.mark.parametrize("run", [main_cli, lnp_cli])
def test_missing_column(tmp_path, run):
    src = tmp_path / "input.csv"
    src.write_text("task_id,target_identifier\nT1,SAMPLE\n")
    assert run(["batch", "-i", str(src), "-o", str(tmp_path / "out.csv")]) == 1

@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_finite_lnp_values(value):
    with pytest.raises(ValueError):
        FrontierPayload("T1", "TARGET", value, 1, "NOMINAL")
