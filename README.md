# Multi-Agent AI Research Pipeline

A production-ready, modular multi-agent system that automates end-to-end research workflows — from web search and AI summarization to compliance validation, professional document generation, and email delivery.

---

## Overview

This project implements a pipeline of four specialized AI agents orchestrated to handle enterprise research tasks with quality assurance and audit trails.

```
User Query
    │
    ▼
┌─────────────────────┐
│   Web Search Agent  │  DuckDuckGo search + Azure OpenAI summarization
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Compliance Guard   │  Citation validation, deduplication, quality scoring
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Document Formatter  │  Generates Markdown, PDF, and Word (.docx) reports
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Emailer Agent     │  Professional HTML email with attachments via SMTP
└─────────────────────┘
```

---

## Features

- **Automated Web Research** — Searches DuckDuckGo (no API key required) and generates AI-powered 2–3 sentence summaries via Azure OpenAI
- **Compliance Validation** — Validates citations, removes duplicate URLs, applies quality scoring (0–1 scale), and enforces approval thresholds
- **Multi-Format Document Generation** — Produces `.md`, `.pdf`, and `.docx` reports with professional formatting and compliance badges
- **Email Delivery** — Sends styled HTML emails with file attachments over SMTP STARTTLS
- **Graceful Degradation** — Runs without Azure OpenAI (search-only mode) and without SMTP (document-only mode)
- **Audit Logging** — Consistent timestamped logs across all agents for full pipeline visibility

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| AI Summarization | Azure OpenAI (GPT-4) |
| Web Search | DuckDuckGo (via BeautifulSoup) |
| PDF Generation | PyMuPDF (`fitz`) |
| Word Documents | `python-docx` |
| Email | `smtplib` with STARTTLS |
| Config Management | `python-dotenv` |

---

## Project Structure

```
multi-agentic-ai/
├── orchestrator.py              # Pipeline controller — coordinates all agents
├── agents/
│   ├── web_search_agent.py      # DuckDuckGo search + AI summarization
│   ├── compliance_guard_agent.py # Content validation & quality scoring
│   ├── document_formatter.py    # PDF / Word / Markdown report generation
│   └── emailer_agent.py         # SMTP email delivery with HTML templates
├── utils/
│   ├── config.py                # Environment-based configuration
│   └── logger.py                # Singleton logger
├── test_phase1.py               # Core utilities tests
├── test_phase2.py               # Web search agent tests
├── test_phase3.py               # Full pipeline integration tests
├── requirements.txt
└── .env.example                 # Template for environment variables
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Azure OpenAI resource (optional — pipeline runs without it)
- SMTP-enabled email account (optional — disables email delivery if absent)

### Installation

```bash
# Clone the repository
git clone https://github.com/maneeshkumar52/multi-agentic-ai.git
cd multi-agentic-ai

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

```env
# SMTP Email Settings
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your_password
FROM_EMAIL=your@email.com
DEFAULT_TO_EMAIL=recipient@email.com

# Azure OpenAI (optional)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Output Directory
OUTPUT_DIR=./outputs
```

---

## Usage

### Run the Full Pipeline

```python
from orchestrator import ResearchOrchestrator

orchestrator = ResearchOrchestrator()
result = orchestrator.run_pipeline(
    query="Python best practices 2024",
    to_email="recipient@example.com",
    send_email=True
)

print(result["summary"])
```

### Run Individual Tests

```bash
# Phase 1: Core utilities
python test_phase1.py

# Phase 2: Web search agent
python test_phase2.py

# Phase 3: Full integration
python test_phase3.py
```

---

## Pipeline Details

### Agent 1 — Web Search Agent

- Queries DuckDuckGo and parses up to 5 results (title, URL, snippet)
- Sends results to Azure OpenAI for a concise 2–3 sentence summary
- Falls back gracefully if Azure OpenAI is unavailable

### Agent 2 — Compliance Guard

- Validates all required fields per citation (title, URL, snippet, source)
- Deduplicates results by URL
- Scores quality on a 0–1 scale based on content richness
- Applies approval rules: minimum 2 results, score ≥ 0.3, ≤50% filtered

### Agent 3 — Document Formatter

- Generates timestamped reports in three formats simultaneously
- PDF: multi-page layout with automatic text wrapping and pagination
- Word: hierarchical headings with centered title and styled body
- Markdown: clean structured output with compliance badge

### Agent 4 — Emailer Agent

- Constructs a professional HTML email with inline CSS styling
- Attaches generated documents (validates file existence before attaching)
- Delivers over SMTP STARTTLS with full error handling

---

## Testing

The three-phase test suite validates each layer progressively:

| Phase | Scope | Command |
|-------|-------|---------|
| Phase 1 | Config, Logger, environment loading | `python test_phase1.py` |
| Phase 2 | Web search, AI summary, result parsing | `python test_phase2.py` |
| Phase 3 | Full pipeline integration | `python test_phase3.py` |

---

## Security Notes

- Credentials are loaded exclusively from `.env` (never hardcoded)
- `.env` is excluded from version control via `.gitignore`
- Email transmission uses STARTTLS encryption
- Output files are excluded from the repository

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Maneesh Kumar**  
[GitHub](https://github.com/maneeshkumar52)
