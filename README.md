# Multi-Agentic AI

Professional-grade multi-agent research and governance application with a local-first Streamlit interface, modular service orchestration, and production-friendly operational workflow.

## 1. Executive Overview

This repository provides:
- Streamlit-based operator UI
- Modular orchestration and domain logic
- Configurable AI runtime integrations (local and/or cloud)
- Artifacts and output persistence for reproducible runs

## 2. Architecture

### 2.1 Logical Architecture

```txt
User / Operator
      |
      v
Streamlit UI Layer
      |
      +--> Orchestration Layer
      +--> AI Adapter Layer (Ollama/OpenAI)
      +--> Retrieval / Processing Layer
      +--> Persistence Layer (data/, outputs/)
```

### 2.2 Runtime Components
- UI Process: Streamlit app
- Model Runtime: configurable local/cloud adapter
- Storage: local filesystem artifacts
- Validation: tests and smoke checks

## 3. Repository Structure

```txt
multi-agentic-ai/
  orchestrator.py
  config.yaml or .env.example
  agents/ or pipeline modules
  data/ or outputs/
  tests/ or smoke_test.py
  requirements.txt
```

## 4. Prerequisites

- Python 3.10+
- pip 23+
- Git
- Ollama or configured model runtime when required

## 5. Local Setup

1. Clone repository

```bash
git clone https://github.com/maneeshkumar52/multi-agentic-ai.git
cd multi-agentic-ai
```

2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Configure runtime

```bash
cp .env.example .env 2>/dev/null || true
```

## 6. Run the Application

```bash
streamlit run orchestrator.py
```

UI endpoint:
- http://localhost:8501

## 7. Validation and Test Flow

1. Syntax validation

```bash
python3 -m compileall -q .
```

2. Tests

```bash
pytest -q 2>/dev/null || true
```

3. Smoke checks

```bash
python smoke_test.py 2>/dev/null || true
```

## 8. Troubleshooting

- Streamlit command not found:
  - Activate .venv
  - Reinstall requirements
- Model runtime unavailable:
  - Start configured local runtime or set cloud credentials
- Empty outputs:
  - Verify configured folders and file permissions

## 9. Production Readiness Checklist

- [ ] Config externalized
- [ ] Secrets managed securely
- [ ] Logging enabled
- [ ] Smoke tests pass
- [ ] Deployment health checks defined

## 10. License

See LICENSE in this repository.
