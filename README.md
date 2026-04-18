# Multi-Agentic AI

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Agents](https://img.shields.io/badge/Agents-4-orange)

A modular multi-agent AI pipeline for automated web research, compliance validation, document generation, and email delivery — powered by Azure OpenAI and orchestrated through a deterministic four-stage pipeline.

## Architecture

```
User Query
    │
    ▼
┌──────────────────────────────┐
│    PipelineOrchestrator      │
│    (orchestrator.py)         │
│                              │
│  Stage 1 ──► WebSearchAgent  │──► Bing/Web scraping + AI summary
│       │                      │
│  Stage 2 ──► ComplianceGuard │──► Citation check, PII scan, quality score
│       │                      │
│  Stage 3 ──► DocFormatter    │──► Markdown + PDF + DOCX generation
│       │                      │
│  Stage 4 ──► EmailerAgent    │──► SMTP delivery with attachments
└──────────────────────────────┘
    │
    ▼
outputs/
├── search_report_YYYYMMDD.md
├── search_report_YYYYMMDD.pdf
└── search_report_YYYYMMDD.docx
```

## Key Features

- **4-Agent Pipeline** — WebSearch → Compliance → Document → Email, each agent is independent and testable
- **Azure OpenAI Integration** — Optional AI-powered summarization of search results (runs without it too)
- **Compliance Guard** — Validates citations, strips PII patterns, enforces quality score threshold (0.30 minimum)
- **Multi-Format Output** — Generates Markdown, PDF (via PyMuPDF), and DOCX (via python-docx) reports
- **Email Delivery** — SMTP-based email with file attachments using modern `EmailMessage` API
- **Web Scraping** — BeautifulSoup-based content extraction with configurable result count
- **Structured Logging** — Per-agent activity logging with timestamps via `Logger` utility

## Step-by-Step Flow

### Step 1: User Submits Query
The user provides a research topic and optional parameters (result count, email toggle, recipient).

### Step 2: Configuration Validation
`PipelineOrchestrator.validate_configuration()` checks Azure OpenAI credentials, SMTP config, and output directory access.

### Step 3: Web Search (WebSearchAgent)
`WebSearchAgent.search(query, num_results)` scrapes web results, extracts content with BeautifulSoup, and optionally generates AI summaries via Azure OpenAI.

### Step 4: Compliance Validation (ComplianceGuardAgent)
`ComplianceGuardAgent.validate(search_result)` runs three checks:
1. **Citation validation** — verifies URLs are reachable and properly formatted
2. **PII detection** — scans content for personal data patterns using regex
3. **Quality scoring** — computes a composite quality score; rejects results below 0.30

### Step 5: Document Generation (DocumentFormatterAgent)
`DocumentFormatterAgent.format_documents(compliance_result, query)` creates:
- Markdown report with structured sections, citations, and metadata
- PDF via PyMuPDF rendering
- DOCX via python-docx with formatted headings and tables

### Step 6: Email Delivery (EmailerAgent)
If `send_email=True`, `EmailerAgent.send_email(to, subject, body, attachments)` sends an HTML email with generated documents as attachments via SMTP.

### Step 7: Pipeline Result
Returns a structured dict with `pipeline_id`, status per stage, file paths, and quality metrics.

## Repository Structure

```
multi-agentic-ai/
├── orchestrator.py              # PipelineOrchestrator — 4-stage pipeline controller
├── agents/
│   ├── __init__.py
│   ├── web_search_agent.py      # WebSearchAgent — web scraping + AI summary
│   ├── compliance_guard_agent.py # ComplianceGuardAgent — validation + PII scan
│   ├── document_formatter.py    # DocumentFormatterAgent — MD/PDF/DOCX output
│   └── emailer_agent.py         # EmailerAgent — SMTP delivery
├── utils/
│   ├── __init__.py
│   ├── config.py                # Config — env-driven settings
│   └── logger.py                # Logger — structured per-agent logging
├── outputs/                     # Generated reports (gitignored)
├── test_phase1.py               # Phase 1 tests — agent initialization
├── test_phase2.py               # Phase 2 tests — pipeline execution
├── test_phase3.py               # Phase 3 tests — end-to-end validation
├── .env.example                 # Environment variable template
└── requirements.txt
```

## Quick Start

```bash
# Clone
git clone https://github.com/maneeshkumar52/multi-agentic-ai.git
cd multi-agentic-ai

# Virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your SMTP and optional Azure OpenAI credentials

# Run the pipeline
python orchestrator.py
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `SMTP_HOST` | Yes | SMTP server hostname |
| `SMTP_PORT` | Yes | SMTP port (587 for TLS) |
| `SMTP_USER` | Yes | SMTP username |
| `SMTP_PASSWORD` | Yes | SMTP password |
| `FROM_EMAIL` | Yes | Sender email address |
| `AZURE_OPENAI_API_KEY` | No | Azure OpenAI key (AI summaries disabled without it) |
| `AZURE_OPENAI_ENDPOINT` | No | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | No | Model deployment name (e.g., gpt-4) |
| `OUTPUT_DIR` | No | Output directory (default: `./outputs`) |

## Testing

```bash
# Phase 1 — Agent initialization
python test_phase1.py

# Phase 2 — Pipeline execution
python test_phase2.py

# Phase 3 — End-to-end validation
python test_phase3.py
```

## Output Formats

| Format | Library | Description |
|--------|---------|-------------|
| Markdown | Built-in | Structured report with citations and metadata |
| PDF | PyMuPDF | Rendered from markdown content |
| DOCX | python-docx | Formatted with headings, tables, and styles |

## License

MIT
