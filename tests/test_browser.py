"""Static UI syntax and security regression checks."""
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "web" / "index.html"


def test_browser_ui_has_no_fabricated_results_or_external_scripts():
    html = HTML.read_text(encoding="utf-8")
    assert 'id="measure-form"' in html
    assert 'id="audit-form"' in html
    assert 'id="export"' in html
    assert "HMAC_SHA256_e83" not in html
    assert "DOSSIER-SIM" not in html
    assert "<script src=" not in html.lower()
    assert "innerHTML" not in html


def test_browser_javascript_syntax():
    if not shutil.which("node"):
        pytest.skip("Node.js is unavailable")
    html = HTML.read_text(encoding="utf-8")
    script = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
    assert script, "Inline JavaScript not found"
    result = subprocess.run(
        ["node", "--check", "-"],
        input=script.group(1), text=True,
        capture_output=True, check=False, timeout=10,
    )
    assert result.returncode == 0, result.stderr
