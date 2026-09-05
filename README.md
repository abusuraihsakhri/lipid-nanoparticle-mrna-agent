# Lipid Nanoparticle Mrna Agent

> **Domain:** Computational Biology & AI Drug Discovery
> **Reference Guidelines & Standards:** `wwPDB, IUPAC & CLSI Computational Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Lipid Nanoparticle Mrna Agent** is an advanced analytical and computational platform implementing LNP N/P ratio, apparent pKa & mRNA encapsulation efficiency formulator. It provides multi-agent consensus evaluation with cryptographic audit trails and zero-PHI outbound protection.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Multi-Agent Consensus**: Three specialized workers (QC, Safety, Protocol Conformance) evaluate each task.
- **HMAC-SHA256 Audit Trail**: Cryptographically chained, tamper-evident logging.
- **Zero-PHI Outbound Guard**: Blocks SSNs, MRNs, phone numbers, and patient identifiers.

---

## 💻 Installation

```bash
pip install -e .
```

---

## 🚀 CLI Quickstart & Usage

### 1. Single Task Evaluation (Audit)
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Parameter | Description | Default |
|:----------|:------------|:--------|
| `--task-id` | Unique task/case identifier | `TASK-2026-001` |
| `--target` | Target entity or specimen identifier | `KEY-TARGET-01` |
| `--primary` | Primary domain measurement (float) | `28.5` |
| `--secondary` | Secondary kinetic/confidence score (float) | `14.2` |
| `--critical` | Flag as critical/emergency escalation | `False` |
| `--status` | Status descriptor (NOMINAL, DISCORDANT, etc.) | `DISCORDANT` |

### Input Data Schema (CSV Batch)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary metric value | Optional (default: 5.0) |
| `is_critical_flag` | Critical flag (true/false) | Optional (default: false) |
| `status_descriptor` | Status descriptor | Optional (default: NOMINAL) |

---

## 🔧 LNP Formulator Subpackage

The `lnp_formulator` module provides specialized LNP formulation calculations:

```bash
python -m lnp_formulator.cli audit --task-id LNP-001 --primary 29.4 --secondary 15.1
python -m lnp_formulator.cli chat "What standard is applied?"
python -m lnp_formulator.cli batch -i sample.csv -o batch_results.csv
python -m lnp_formulator.cli serve --port 8000
```

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable for persistent audit integrity across sessions:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY="your-secure-random-key"

# Windows
set AUDIT_SECRET_KEY=your-secure-random-key
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t lipid-nanoparticle-mrna-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key lipid-nanoparticle-mrna-agent
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
lipid-nanoparticle-mrna-agent/
├── agents/                  # Core agent modules
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Multi-agent orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── llm_factory.py      # LLM provider factory
│   ├── learning.py         # Bayesian calibration engine
│   ├── metrics.py          # Prometheus metrics
│   └── streamer.py         # WebSocket telemetry
├── lnp_formulator/         # LNP formulation subpackage
│   ├── agents.py           # Specialized LNP agents
│   ├── engine.py           # Core calculation engine
│   ├── models.py           # LNP data models
│   ├── cli.py              # LNP CLI interface
│   └── server.py           # LNP FastAPI server
├── tests/                  # Test suite
├── web/                    # Web operations console
├── cli.py                  # Main CLI entry point
├── simulator.py            # High-throughput simulator
├── enrichment.py           # Domain enrichment features
├── pyproject.toml          # Project configuration
├── Dockerfile              # Container build
└── docker-compose.yml      # Container orchestration
```
