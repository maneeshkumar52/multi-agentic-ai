# Multi-Agentic AI

Enterprise-style multi-agent pipeline for automated analysis, governance checks, and report generation.

## Architecture

- Orchestrator: Coordinates pipeline phases and agent sequencing
- Specialist Agents: Perform retrieval, analysis, and transformation tasks
- Compliance Gate: Validates quality, policy, and output readiness
- Publication Layer: Generates artifacts under `outputs/`

## Repository Structure

```txt
multi-agentic-ai/
  orchestrator.py
  agents/
  utils/
  outputs/
  test_phase*.py
  requirements.txt
```

## Prerequisites

- Python 3.10+
- pip 23+
- Optional API keys for external model providers

## Setup and Execution

1. Clone and enter repository

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

4. Configure environment

```bash
cp .env.example .env 2>/dev/null || true
```

5. Execute pipeline validation phases

```bash
python test_phase1.py
python test_phase2.py
python test_phase3.py
```

## Troubleshooting

- Dependency mismatch: recreate virtual environment and reinstall
- Missing secrets: verify `.env` values for model/email providers
- Report generation errors: ensure output directory exists and is writable

## License

See `LICENSE` in this repository.