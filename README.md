# Multi-Agent AI Research Pipeline

An architecture-driven, enterprise-style Python pipeline for automated research, compliance enforcement, report generation, and optional email delivery.

## Why This Project

This system is designed for teams that need:

- Repeatable research workflows.
- Validated source handling with governance checks.
- Audit-friendly outputs (Markdown, PDF, DOCX).
- A modular multi-agent structure that can be evolved without rewriting the whole flow.

## System Architecture

### Logical Architecture

```text
Input Query
    |
    v
PipelineOrchestrator
    |
    +--> WebSearchAgent
    |      - DuckDuckGo retrieval
    |      - Optional Azure OpenAI summary
    |
    +--> ComplianceGuardAgent (quality gate)
    |      - citation validation
    |      - duplicate URL elimination
    |      - quality scoring and approval decision
    |
    +--> DocumentFormatterAgent
    |      - Markdown report
    |      - PDF report
    |      - DOCX report
    |
    +--> EmailerAgent (optional)
           - HTML email body
           - attachments from generated artifacts
```

### Execution Flow

1. Orchestrator validates configuration and output directory readiness.
2. Web search agent fetches and normalizes search results.
3. Compliance guard enforces quality and approval rules.
4. Formatter produces timestamped artifacts.
5. Emailer sends approved artifacts when enabled.

### Governance Pattern

The pipeline follows a gate-based model:

- Stage 1 (acquisition): gather external inputs.
- Stage 2 (governance): enforce trust and quality thresholds.
- Stage 3 (publication): produce human-consumable reports.
- Stage 4 (distribution): controlled delivery to stakeholders.

This model makes the pipeline suitable for AI architecture reviews where data provenance and output quality matter.

## Key Capabilities

- Web retrieval from DuckDuckGo HTML endpoint.
- Optional Azure OpenAI summarization for concise synthesis.
- Structural citation checks and source de-duplication.
- Quality score computation with explicit thresholds.
- Multi-format report packaging for different stakeholder formats.
- Optional secure SMTP delivery using STARTTLS.
- Full pipeline traceability using structured logs.

## Technology Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.10+ |
| Search Retrieval | requests + BeautifulSoup |
| AI Summarization | Azure OpenAI via openai.AzureOpenAI |
| Compliance Logic | Custom Python validation/scoring rules |
| Document Generation | Markdown, PyMuPDF, python-docx |
| Email Transport | smtplib + EmailMessage + STARTTLS |
| Configuration | python-dotenv + env variables |

## Project Structure

```text
multi-agentic-ai/
|- orchestrator.py
|- agents/
|  |- web_search_agent.py
|  |- compliance_guard_agent.py
|  |- document_formatter.py
|  |- emailer_agent.py
|- utils/
|  |- config.py
|  |- logger.py
|- test_phase1.py
|- test_phase2.py
|- test_phase3.py
|- requirements.txt
|- .env.example
|- outputs/
```

## Setup Steps

### 1) Clone and Enter Workspace

```bash
git clone https://github.com/maneeshkumar52/multi-agentic-ai.git
cd multi-agentic-ai
```

### 2) Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 3) Install Dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure Environment

```bash
cp .env.example .env
```

Edit .env with your values:

```env
# SMTP Email Settings
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your_password
FROM_EMAIL=your@email.com
DEFAULT_TO_EMAIL=recipient@email.com

# Azure OpenAI (optional)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Output Directory
OUTPUT_DIR=./outputs
```

## How to Run

### Python Entry Example

```python
from orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()

result = orchestrator.run_pipeline(
    query="enterprise ai governance architecture",
    num_results=5,
    send_email=False,
    recipient_email=None,
    filename_prefix="search_report"
)

print(orchestrator.get_pipeline_summary(result))
```

### With Email Delivery Enabled

```python
from orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()

result = orchestrator.run_pipeline(
    query="ai operating model for architecture teams",
    num_results=5,
    send_email=True,
    recipient_email="recipient@example.com",
    filename_prefix="search_report"
)

print(result["status"])
```

## Testing and Validation

Run in sequence for progressive confidence:

```bash
python test_phase1.py
python test_phase2.py
python test_phase3.py
```

Test phases:

- Phase 1: config and utility validation.
- Phase 2: web search and summary behavior.
- Phase 3: end-to-end multi-agent integration.

## Compliance and Quality Rules

The compliance guard enforces:

- Required fields: title, url, snippet, source.
- Source type validation (DuckDuckGo entries).
- URL validation and duplicate elimination.
- Minimum quality threshold of 0.3.
- Minimum validated result count of 2.
- Rejection if too many records are filtered.

If governance rules fail, pipeline status becomes rejected and downstream publication is blocked.

## Operational Notes

- Azure OpenAI is optional. If not configured, search still works and summary is skipped.
- SMTP is optional. If disabled, reports are generated without delivery.
- Output artifacts are timestamped and stored under the configured output directory.
- Logs are emitted per agent for easier troubleshooting and observability.

## Security and Production Guidance

- Keep credentials only in .env and never commit secrets.
- Use app-specific SMTP credentials where possible.
- Consider secret management via environment injection in CI/CD.
- Add periodic dependency and security scanning before production rollout.

## Author

Maneesh Kumar

- GitHub: https://github.com/maneeshkumar52

## License

MIT License. See LICENSE.
