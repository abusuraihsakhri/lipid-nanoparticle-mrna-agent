# Lipid Nanoparticle mRNA Agent

Research utilities for lipid nanoparticle (LNP) formulation measurements and generic rule-based task screening. This repository contains a static browser calculator, two Python CLI workflows, and FastAPI endpoints.

## Browser calculator

The `web/index.html` page works without a Python server. Open it in a current browser, or serve the repository root as a static site. The root `index.html` redirects to the calculator for static hosting.

The browser performs four **deterministic, input-derived** calculations:

- **N/P ratio:** ionizable nitrogen amount divided by RNA phosphate amount, in identical molar units.
- **Encapsulation efficiency (%):** `100 × (total mRNA − free mRNA) / total mRNA`, using equal measurement units.
- **Ideal protonated fraction:** `1 / (1 + 10^(pH − pKa))` for a monoprotic basic group, using a **supplied, experimentally measured** pKa.
- **DLS cumulants PDI (optional):** second cumulant divided by squared mean decay rate, using compatible units.

Inputs are checked for nonfinite values, invalid denominators, and inconsistent free/total mRNA. Results can be exported as JSON. Calculations run locally in the browser, with no uploads or external JavaScript dependencies.

**Scientific scope:** these calculations do not measure or predict transfection, in-vivo biodistribution, safety, stability, or clinical suitability. The protonation equation is an idealized model, not a method for determining pKa from raw fluorescence measurements. The `enrichment.py` modules are generic threshold-based demonstrations, not validated DoE, PBPK, or ML predictors.

## Python installation

Python 3.10–3.12 are tested in CI. Python 3.9+ is declared supported.

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

The package provides three executable commands: `lipid-nanoparticle-mrna-agent` (generic research screening), `lnp-formulator` (LNP-specific threshold screening and measurement calculations), and the legacy `lipid-nanoparticle-mrna-engine` alias.

### Measured LNP calculation

```bash
python -m lnp_formulator.cli measure \
  --nitrogen 60 --phosphate 10 \
  --total-mrna 100 --free-mrna 8 \
  --ph 6.5 --pka 6.8
```

The CLI emits a JSON object containing N/P ratio, encapsulation efficiency, and ideal protonated fraction.

### Existing generic task evaluation

```bash
python cli.py audit --task-id TASK-001 --target SAMPLE-001 \
  --primary 28.5 --secondary 14.2 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py chat "What is the system status?"
python cli.py verify-audit
```

The distinct LNP-specific threshold screener is available through `python -m lnp_formulator.cli audit` and `python -m lnp_formulator.cli batch`. These audit modes compare **generic metrics** against hard-coded rule thresholds; they do not calculate N/P, pKa, or encapsulation efficiency and should not be interpreted as clinical or GMP conformance checks.

## API and local web interface

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` to use the packaged calculator and the optional **server audit** panel. Documentation is available at `/docs`.

| Endpoint | Purpose |
|---|---|
| `GET /` | Browser calculator and audit client |
| `GET /health` | Health metadata |
| `POST /api/measure` | Deterministic LNP measurements |
| `POST /api/audit` | Generic three-worker threshold audit |
| `POST /api/chat` | Deterministic mock response (not an external LLM) |
| `GET /api/audit/logs` | In-memory HMAC audit entries and integrity check |
| `GET /metrics` | JSON operational counters, not Prometheus exposition |

The optional browser audit sends data to `/api/audit` **at the page's origin**. It requires a running API server; static-only hosting does not run this feature and does not fabricate a result.

## Security and privacy

- The Python audit ledger signs entries with HMAC-SHA256 and verifies every signature plus the chain links. The ledger is held **in process memory**, not a durable external audit store.
- Set `AUDIT_SECRET_KEY` to a long, random secret to keep a stable signing key across process starts. If omitted, the application generates a new, ephemeral key. Never commit an actual key.
- A **best-effort regular-expression guard** detects selected patterns resembling patient identifiers. It is **not** a comprehensive PHI de-identification or HIPAA-compliance solution. Do not submit patient data.
- The static calculator computes locally. Server audit requests transmit the submitted fields to the configured API. Both APIs and the in-memory task registries are intended for controlled local use; no authentication is provided.
- LLM provider names currently map to a deterministic mock. External Claude, OpenAI, and Ollama inference is **not implemented**.

To build and run the service with Docker Compose, first supply a key in the environment:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

Docker publishes port 8000 by default; do not expose it publicly without authentication, authorization, transport security, and appropriate network controls.

## Testing and deployment

```bash
python -m pip install -e ".[test]"
python -m compileall -q agents lnp_formulator tests cli.py enrichment.py simulator.py
python -m pytest -q
python simulator.py 100
```

CI tests Python 3.10, 3.11, and 3.12. The standalone HTML page is suitable for static hosting, including GitHub Pages; **an active Pages deployment has not been verified**. Static hosts cannot execute the Python FastAPI server.

Modern Chrome, Firefox, Safari, and Edge support the browser page's standard JavaScript APIs. No browser-based Python or Pyodide runtime is required because the standalone calculations are implemented in JavaScript.

## License

MIT — see [LICENSE](LICENSE).
