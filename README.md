# Multi-Agentic AI — Production Multi-Agent Research Pipeline

> **Maneesh Kumar**
> A modular 4-agent pipeline that automates web research, compliance validation, document generation, and email delivery. Powered by DuckDuckGo search, Azure OpenAI (optional), and SMTP — runs fully offline without API keys.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-0078D4.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Pipeline Execution — Annotated Terminal Output](#pipeline-execution--annotated-terminal-output)
3. [Design Decisions](#design-decisions)
4. [Data Contracts](#data-contracts)
5. [Features](#features)
6. [Prerequisites](#prerequisites)
7. [Setup](#setup)
8. [Running the Pipeline](#running-the-pipeline)
9. [Configuration Reference](#configuration-reference)
10. [Project Structure](#project-structure)
11. [Testing](#testing)
12. [Troubleshooting](#troubleshooting)
13. [Azure Production Mapping](#azure-production-mapping)
14. [Production Checklist](#production-checklist)

---

## System Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT RESEARCH PIPELINE                      │
│                                                                       │
│  User Query                                                           │
│       │                                                               │
│       ▼                                                               │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  PipelineOrchestrator                                          │   │
│  │    • Validates configuration (SMTP, Azure OpenAI, output dir)  │   │
│  │    • Assigns pipeline UUID + timestamp                         │   │
│  │    • Manages stage-by-stage execution                          │   │
│  │    • Generates human-readable summary on completion            │   │
│  └────────────────────┬───────────────────────────────────────────┘   │
│                       │                                               │
│       ┌───────────────┼───────────────┬───────────────┐               │
│       ▼               ▼               ▼               ▼               │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────┐        │
│  │ STAGE 1  │  │   STAGE 2    │  │  STAGE 3  │  │ STAGE 4  │        │
│  │          │  │              │  │           │  │          │        │
│  │ WebSearch│─▶│  Compliance  │─▶│ Document  │─▶│ Emailer  │        │
│  │  Agent   │  │  GuardAgent  │  │ Formatter │  │  Agent   │        │
│  │          │  │              │  │   Agent   │  │          │        │
│  │ DuckDuck │  │ Citation     │  │           │  │ SMTP     │        │
│  │ Go HTML  │  │ validation   │  │ Markdown  │  │ starttls │        │
│  │ scraping │  │ Dedup        │  │ PDF       │  │ HTML body│        │
│  │ + Azure  │  │ Quality      │  │ DOCX      │  │ + attach │        │
│  │ OpenAI   │  │ scoring      │  │           │  │          │        │
│  │ summary  │  │ Approval     │  │ outputs/  │  │ Optional │        │
│  │(optional)│  │ gate         │  │           │  │          │        │
│  └──────────┘  └──────────────┘  └───────────┘  └──────────┘        │
│       │               │               │               │               │
│       ▼               ▼               ▼               ▼               │
│  search_result   compliance_result  doc_result    email_result        │
│  {status,        {approved,         {md_path,     {status,            │
│   results[],      cleaned_results,   pdf_path,     recipient,         │
│   ai_summary}     quality_score,     docx_path,    attachments}       │
│                   issues[]}          files[]}                         │
│                                                                       │
│  Cross-Cutting:                                                       │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │  Logger (singleton)  │  Config (.env)  │  pipeline UUID     │     │
│  └──────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

```
orchestrator.py
  └── PipelineOrchestrator
        ├── validate_configuration()    — Pre-flight check: SMTP, Azure OpenAI, output dir
        ├── run_pipeline()              — Sequential 4-stage execution with error propagation
        └── get_pipeline_summary()      — Human-readable stage-by-stage result

agents/
  ├── web_search_agent.py
  │     └── WebSearchAgent
  │           ├── search(query, num_results)  — DuckDuckGo HTML scrape + result parsing
  │           └── _generate_ai_summary()      — Azure OpenAI GPT-4 summarisation (optional)
  │
  ├── compliance_guard_agent.py
  │     └── ComplianceGuardAgent
  │           ├── validate(search_result)     — Full compliance pipeline
  │           ├── _validate_citations()       — URL, title, snippet structure check
  │           ├── _remove_duplicates()        — URL-based deduplication
  │           ├── _validate_ai_summary()      — Summary coherence check
  │           └── _check_content_quality()    — Quality scoring (0.0–1.0)
  │
  ├── document_formatter.py
  │     └── DocumentFormatterAgent
  │           ├── format_documents()          — Orchestrates all format generation
  │           ├── _generate_markdown()        — Structured .md with AI summary + results
  │           ├── _generate_pdf()             — PyMuPDF-based PDF rendering
  │           └── _generate_word()            — python-docx DOCX generation
  │
  └── emailer_agent.py
        └── EmailerAgent
              ├── send_email()                    — SMTP/TLS with attachments
              ├── send_search_results_email()      — Professional HTML body + compliance badge
              └── _generate_html_body()            — Responsive HTML email template
```

---

## Pipeline Execution — Annotated Terminal Output

### Use Case 1: Full Pipeline (Search + Compliance + Documents)

**Query:** *"Python programming best practices 2025"*

```
═══════════════════════════════════════════════════════════════
  MULTI-AGENT RESEARCH PIPELINE
  Pipeline ID: a3f8c2e1-9d4b-4a6f-b8c1-7e2d5f9a3b1c
═══════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────
  Configuration Validation
────────────────────────────────────────────────────────────
  ✅  SMTP_HOST:     smtp.office365.com:587
  ✅  FROM_EMAIL:    configured
  ✅  OUTPUT_DIR:    ./outputs (writable)
  ⚠️  Azure OpenAI:  not configured — AI summaries disabled

────────────────────────────────────────────────────────────
  STAGE 1: WebSearchAgent — DuckDuckGo Search
────────────────────────────────────────────────────────────
  [WebSearchAgent] Starting search for: Python programming best practices 2025
  [WebSearchAgent] Scraping DuckDuckGo HTML results...
  [WebSearchAgent] Parsed 5 results from search page

  Result 1: "Python Best Practices for 2025"
    URL:     https://realpython.com/python-best-practices/
    Snippet: "Follow these proven patterns for clean, maintainable
             Python code including type hints, virtual environments..."
    Source:  DuckDuckGo

  Result 2: "PEP 8 — Style Guide for Python Code"
    URL:     https://peps.python.org/pep-0008/
    Snippet: "This document gives coding conventions for the Python
             code comprising the standard library..."
    Source:  DuckDuckGo

  [... 3 more results ...]

  AI Summary: None (Azure OpenAI not configured)

  ✅  Web search complete: 5 results found

────────────────────────────────────────────────────────────
  STAGE 2: ComplianceGuardAgent — Validation
────────────────────────────────────────────────────────────
  [ComplianceGuardAgent] Starting validation
  [ComplianceGuardAgent] Step 1: Citation validation — 5/5 pass
  [ComplianceGuardAgent] Step 2: Duplicate removal — 0 duplicates
  [ComplianceGuardAgent] Step 3: AI summary validation — skipped (no summary)
  [ComplianceGuardAgent] Step 4: Quality scoring — 0.85

  ✅  Validation complete: approved (5/5 results, score: 0.85)

────────────────────────────────────────────────────────────
  STAGE 3: DocumentFormatterAgent — Document Generation
────────────────────────────────────────────────────────────
  [DocumentFormatterAgent] Starting document generation
  [DocumentFormatterAgent] Generating Markdown...  ✅
  [DocumentFormatterAgent] Generating PDF...       ✅
  [DocumentFormatterAgent] Generating DOCX...      ✅

  Files created:
    📄  outputs/search_report_20250103_110510.md
    📄  outputs/search_report_20250103_110510.pdf
    📄  outputs/search_report_20250103_110510.docx

  ✅  Documents generated: MD=True, PDF=True, DOCX=True

────────────────────────────────────────────────────────────
  STAGE 4: EmailerAgent — Delivery (skipped)
────────────────────────────────────────────────────────────
  ⏭️  Email delivery not requested

════════════════════════════════════════════════════════════
  PIPELINE SUMMARY
════════════════════════════════════════════════════════════
  Pipeline ID:  a3f8c2e1-9d4b-4a6f-b8c1-7e2d5f9a3b1c
  Query:        Python programming best practices 2025
  Status:       success

  Stages:
    Web Search:          success (5 results)
    Compliance Guard:    Approved (Score: 0.85)
    Document Formatting: success (3 files)
    Email:               skipped

  ✓ Pipeline completed with compliance validation
```

---

### Use Case 2: Compliance Rejection (Quality Gate)

**Query:** *""* (empty query)

```
────────────────────────────────────────────────────────────
  STAGE 1: WebSearchAgent
────────────────────────────────────────────────────────────
  [WebSearchAgent] Starting search for: (empty)
  [WebSearchAgent] Error: Empty query

  ✗  Web search failed

────────────────────────────────────────────────────────────
  PIPELINE RESULT
────────────────────────────────────────────────────────────
  Status:  error
  Stage:   web_search
  Error:   Web search failed
```

---

### Use Case 3: Full Pipeline with Email Delivery

**Query:** *"AI trends 2025"* with `send_email=True`

```
────────────────────────────────────────────────────────────
  STAGE 4: EmailerAgent — Delivery
────────────────────────────────────────────────────────────
  [EmailerAgent] Sending email to: recipient@company.com
  [EmailerAgent] Subject: Search Results Report - Quality Score: 0.82
  [EmailerAgent] Attachments: 3 files
    📎  search_report_20250103_142030.md
    📎  search_report_20250103_142030.pdf
    📎  search_report_20250103_142030.docx
  [EmailerAgent] SMTP connection: smtp.office365.com:587 (STARTTLS)

  ✅  Email sent successfully to: recipient@company.com

════════════════════════════════════════════════════════════
  PIPELINE SUMMARY
════════════════════════════════════════════════════════════
  Web Search:          success (5 results)
  Compliance Guard:    Approved (Score: 0.82)
  Document Formatting: success (3 files)
  Email:               success

  ✓ Pipeline completed with compliance validation
```

---

## Design Decisions

### 1. Why a Sequential Pipeline Over Parallel Agents?

| Concern | Parallel Agents | Sequential Pipeline |
|---|---|---|
| **Data dependency** | Each agent needs independent inputs | Each stage feeds the next — natural chain |
| **Compliance** | Must validate before formatting | Stage 2 gates Stage 3 — rejected content never reaches documents |
| **Error propagation** | Complex coordination | Simple: any stage failure stops the pipeline |
| **Debugging** | Non-deterministic execution order | Deterministic: always Stage 1 → 2 → 3 → 4 |
| **Email safety** | Risk of sending unvalidated content | Email agent only receives compliance-approved content |

The pipeline topology matches the data flow: raw search results are meaningless without compliance validation, and documents are meaningless without approved content.

### 2. DuckDuckGo Over API-Based Search

- **No API key required** — reduces onboarding friction to zero
- **HTML scraping** via BeautifulSoup — works behind most firewalls
- **Redirect resolution** — handles DuckDuckGo's `uddg=` parameter for clean URLs
- **Snippet extraction** — parses `result__body` divs, limits to 300 chars
- **Trade-off:** Rate-limited and less structured than Google/Bing APIs. Acceptable for research pipelines with 3–10 results per query.

### 3. Compliance Guard as a Hard Gate

The `ComplianceGuardAgent` is not a filter — it is a **gate**. If validation fails, the pipeline stops and returns a `rejected` status. No documents are generated, no emails are sent.

Validation stages:
1. **Citation validation** — every result must have `title`, `url`, `snippet`, `source`
2. **Deduplication** — URL-based duplicate removal
3. **AI summary validation** — coherence check against cleaned results
4. **Quality scoring** — composite score (0.0–1.0); threshold at 0.30
5. **Minimum results check** — at least 2 valid results required

If cleaned results drop below 50% of originals, an issue is flagged.

### 4. Azure OpenAI Is Optional

The pipeline runs completely without Azure OpenAI. When configured:
- `WebSearchAgent` generates an AI summary of search results using GPT-4
- `ComplianceGuardAgent` validates the AI summary against source material

When not configured:
- AI summary is `None`
- All other pipeline stages function identically
- Documents are generated from raw search results only

This design means **zero cloud dependency** for the core pipeline.

### 5. Multi-Format Document Generation

| Format | Library | Purpose |
|---|---|---|
| Markdown | Built-in string formatting | Version control, quick review, README embedding |
| PDF | PyMuPDF (`fitz`) | Professional distribution, archival |
| DOCX | `python-docx` | Enterprise sharing, MS Office integration |

All three formats are generated in parallel from the same compliance-approved content. Each includes:
- Query and timestamp header
- AI summary (if available)
- Numbered search results with titles, URLs, and snippets
- Compliance quality score badge

---

## Data Contracts

All inter-agent communication uses structured dictionaries with consistent keys. The pipeline never passes raw strings between stages.

### WebSearchAgent → ComplianceGuardAgent

```python
# search_result
{
    'status':        'success',          # 'success' | 'error'
    'query':         str,                # Original search query
    'results': [                         # List of search results
        {
            'title':   str,              # Page title
            'url':     str,              # Resolved URL (no DuckDuckGo redirects)
            'snippet': str,              # First 300 chars of page content
            'source':  'DuckDuckGo'      # Source identifier
        }
    ],
    'total_results': int,                # Count of parsed results
    'sources':       List[str],          # Unique source domains
    'ai_summary':    Optional[str]       # Azure OpenAI summary or None
}
```

### ComplianceGuardAgent → DocumentFormatterAgent

```python
# compliance_result
{
    'status':             'approved',    # 'approved' | 'rejected'
    'approved':           bool,          # Hard gate flag
    'cleaned_results':    List[dict],    # Citation-validated, deduplicated results
    'validated_summary':  Optional[str], # Validated AI summary or None
    'original_count':     int,           # Results before validation
    'cleaned_count':      int,           # Results after validation
    'issues':             List[str],     # [] if approved, reason strings if rejected
    'quality_score':      float          # 0.0–1.0 composite quality
}
```

### DocumentFormatterAgent → EmailerAgent

```python
# doc_result
{
    'status':            'success',      # 'success' | 'error'
    'markdown_path':     Optional[str],  # Path to .md file
    'pdf_path':          Optional[str],  # Path to .pdf file
    'pdf_generated':     bool,           # PDF generation success
    'docx_path':         Optional[str],  # Path to .docx file
    'docx_generated':    bool,           # DOCX generation success
    'files_created':     List[str],      # All generated file paths
    'content_validated': bool            # True if source was compliance-approved
}
```

### EmailerAgent → Orchestrator

```python
# email_result
{
    'status':            'success',      # 'success' | 'error'
    'recipient':         str,            # Email address
    'attachments_count': int,            # Number of attached files
    'error':             Optional[str]   # Error message if failed
}
```

### PipelineOrchestrator Final Result

```python
# pipeline_result
{
    'pipeline_id':       str,            # UUID for this execution
    'timestamp':         str,            # ISO 8601 timestamp
    'query':             str,            # Original query
    'status':            str,            # 'success' | 'partial_success' | 'error' | 'rejected'
    'stages': {
        'web_search':          dict,     # WebSearchAgent result
        'compliance_guard':    dict,     # ComplianceGuardAgent result
        'document_formatting': dict,     # DocumentFormatterAgent result
        'email':               dict      # EmailerAgent result (if requested)
    },
    'compliance_passed': bool            # True if Stage 2 approved
}
```

---

## Features

### Core Pipeline

| Feature | Description |
|---|---|
| 4-agent sequential pipeline | WebSearch → Compliance → Documents → Email |
| Pipeline UUID tracking | Every execution gets a unique ID for audit trails |
| Configuration validation | Pre-flight checks before any agent runs |
| Stage-by-stage error propagation | Failure at any stage stops downstream processing |
| Human-readable summaries | `get_pipeline_summary()` for terminal + log output |

### Web Search (Stage 1)

| Feature | Description |
|---|---|
| DuckDuckGo HTML scraping | No API key required |
| BeautifulSoup parsing | Structured extraction from `result__a` and `result__body` divs |
| Redirect URL resolution | Resolves `uddg=` parameters to clean URLs |
| Snippet length limiting | Truncates to 300 characters |
| Azure OpenAI AI summary | Optional GPT-4 summarisation of search results |
| Configurable result count | `num_results` parameter (default: 5) |

### Compliance Validation (Stage 2)

| Feature | Description |
|---|---|
| Citation structure validation | Requires `title`, `url`, `snippet`, `source` on every result |
| URL deduplication | Removes duplicate URLs from result set |
| AI summary validation | Coherence check against source material |
| Quality scoring | Composite score 0.0–1.0 with configurable threshold (0.30) |
| Minimum results gate | Requires ≥2 valid results after cleaning |
| 50% retention check | Flags if more than half of results are filtered |
| Hard gate enforcement | Pipeline stops on rejection — no documents generated |

### Document Generation (Stage 3)

| Feature | Description |
|---|---|
| Markdown (.md) | Structured report with headers, AI summary, numbered results |
| PDF (.pdf) | PyMuPDF-rendered professional document |
| Word (.docx) | python-docx formatted enterprise document |
| Timestamped filenames | `search_report_YYYYMMDD_HHMMSS.{ext}` |
| Configurable prefix | Custom filename prefix via `filename_prefix` parameter |
| Output directory | Configurable via `OUTPUT_DIR` env var |

### Email Delivery (Stage 4)

| Feature | Description |
|---|---|
| SMTP with STARTTLS | Secure email delivery |
| HTML email body | Professional responsive template with compliance badge |
| Multi-file attachments | Attaches all generated documents (MD, PDF, DOCX) |
| Quality score badge | Visual compliance indicator in email header |
| File existence validation | Skips missing attachments gracefully |
| Optional execution | Email stage only runs when `send_email=True` |

### Operations

| Feature | Description |
|---|---|
| Singleton logger | Thread-safe, consistent logging across all agents |
| Environment-based config | `.env` file with `python-dotenv` |
| Phase-based testing | 3 test scripts covering utilities, search, and full pipeline |
| Graceful degradation | Pipeline runs without Azure OpenAI, PDF, or DOCX libraries |

---

## Prerequisites

### Required

| Dependency | Version | Check Command |
|---|---|---|
| Python | 3.11+ | `python3 --version` |
| pip | Latest | `pip --version` |
| Git | Any | `git --version` |

### Optional

| Dependency | Purpose | When Needed |
|---|---|---|
| Azure OpenAI | AI summaries | Only for enhanced search summaries |
| SMTP server | Email delivery | Only for Stage 4 (email) |

<details>
<summary><strong>macOS Installation</strong></summary>

```bash
# Python 3.11+
brew install python@3.11

# Git (usually pre-installed)
brew install git

# Verify
python3 --version   # Python 3.11.x or higher
git --version
```

</details>

<details>
<summary><strong>Windows Installation</strong></summary>

1. Download Python from [python.org](https://www.python.org/downloads/)
   — **Check "Add Python to PATH"** during installation
2. Download Git from [git-scm.com](https://git-scm.com/download/win)

```powershell
# Verify
python --version    # Python 3.11.x or higher
git --version
```

</details>

<details>
<summary><strong>Linux (Ubuntu/Debian) Installation</strong></summary>

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git

# Verify
python3 --version
git --version
```

</details>

---

## Setup

### Step 1 — Clone the Repository

```bash
git clone https://github.com/maneeshkumar52/multi-agentic-ai.git
cd multi-agentic-ai
```

### Step 2 — Create a Virtual Environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
```

> Your terminal prompt should now show `(.venv)` at the beginning.

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

```
Installing collected packages:
  ✅  requests           — HTTP client for DuckDuckGo
  ✅  beautifulsoup4     — HTML parsing
  ✅  lxml               — Fast XML/HTML parser backend
  ✅  python-dotenv      — .env file loading
  ✅  openai             — Azure OpenAI client
  ✅  PyMuPDF            — PDF generation
  ✅  python-docx        — DOCX generation
  ✅  markdown2          — Markdown rendering
  ✅  streamlit          — Web UI (optional)
```

### Step 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# SMTP (required for email delivery, optional otherwise)
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your@email.com
DEFAULT_TO_EMAIL=recipient@email.com

# Azure OpenAI (optional — pipeline runs without it)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Output Directory
OUTPUT_DIR=./outputs
```

> **No Azure OpenAI?** Leave the Azure fields empty. The pipeline runs fully without them — AI summaries are simply disabled.

### Step 5 — Verify Setup

```bash
python test_phase1.py
```

```
=== PHASE 1 TESTING ===

1. Testing imports...
✓ Config and Logger imported successfully

2. Testing environment variables...
✓ SMTP_HOST: smtp.office365.com
✓ SMTP_PORT: 587
✓ SMTP_USER: your@email.com
✓ OUTPUT_DIR: outputs

3. Testing OUTPUT_DIR...
✓ OUTPUT_DIR exists and is writable: outputs

4. Testing Logger singleton...
✓ Logger singleton works correctly

5. Testing Config.validate()...
✓ Config.validate() returns empty list

6. Testing Logger methods...
✓ Logger methods work correctly

7. Testing virtual environment...
✓ Using virtual environment

8. Testing PyMuPDF import...
✓ import pymupdf as fitz works

=== RESULTS: 8/8 tests passed ===
✓ PHASE 1 COMPLETE - Core utilities operational
```

---

## Running the Pipeline

### Option 1: Python Script

```python
from orchestrator import PipelineOrchestrator

# Initialize
pipeline = PipelineOrchestrator()

# Run search + compliance + document generation
result = pipeline.run_pipeline(
    query="artificial intelligence trends 2025",
    num_results=5,
    send_email=False
)

# Print summary
print(pipeline.get_pipeline_summary(result))
```

### Option 2: With Email Delivery

```python
result = pipeline.run_pipeline(
    query="cloud computing security best practices",
    num_results=5,
    send_email=True,
    recipient_email="team@company.com",
    filename_prefix="security_report"
)
```

### Option 3: Individual Agents

```python
from agents import WebSearchAgent, ComplianceGuardAgent, DocumentFormatterAgent

# Stage 1: Search
search_agent = WebSearchAgent()
search_result = search_agent.search("Python best practices", num_results=3)

# Stage 2: Validate
compliance = ComplianceGuardAgent()
compliance_result = compliance.validate(search_result)

if compliance_result['approved']:
    # Stage 3: Generate documents
    formatter = DocumentFormatterAgent()
    doc_result = formatter.format_documents(
        compliance_result,
        "Python best practices",
        filename_prefix="python_report"
    )
    print(f"Files created: {doc_result['files_created']}")
else:
    print(f"Rejected: {compliance_result['issues']}")
```

---

## Configuration Reference

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `SMTP_HOST` | For email | — | SMTP server hostname |
| `SMTP_PORT` | For email | `587` | SMTP server port |
| `SMTP_USER` | For email | — | SMTP authentication username |
| `SMTP_PASSWORD` | For email | — | SMTP authentication password |
| `FROM_EMAIL` | For email | — | Sender email address |
| `DEFAULT_TO_EMAIL` | For email | — | Default recipient email |
| `AZURE_OPENAI_API_KEY` | No | — | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | No | — | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_VERSION` | No | — | Azure OpenAI API version |
| `AZURE_OPENAI_DEPLOYMENT` | No | — | Azure OpenAI deployment name |
| `OUTPUT_DIR` | No | `./outputs` | Directory for generated documents |

### Compliance Thresholds

| Parameter | Value | Location |
|---|---|---|
| Minimum quality score | 0.30 | `compliance_guard_agent.py` |
| Minimum valid results | 2 | `compliance_guard_agent.py` |
| Maximum filter ratio | 50% | `compliance_guard_agent.py` |
| Snippet max length | 300 chars | `web_search_agent.py` |

---

## Project Structure

```
multi-agentic-ai/
│
├── orchestrator.py                     ← Pipeline controller
│   └── PipelineOrchestrator            ← Config validation + 4-stage execution + summary
│
├── agents/
│   ├── __init__.py                     ← Agent registry (WebSearch, Compliance, Formatter, Emailer)
│   ├── web_search_agent.py             ← DuckDuckGo HTML scraping + Azure OpenAI summary
│   ├── compliance_guard_agent.py       ← Citation validation + dedup + quality gate
│   ├── document_formatter.py           ← Markdown + PDF + DOCX generation
│   └── emailer_agent.py               ← SMTP/TLS email with HTML body + attachments
│
├── utils/
│   ├── __init__.py                     ← Exports Config + Logger
│   ├── config.py                       ← Environment-based configuration (python-dotenv)
│   └── logger.py                       ← Singleton logger with agent activity tracking
│
├── outputs/                            ← Generated documents (gitignored)
│   ├── search_report_*.md              ← Markdown reports
│   ├── search_report_*.pdf             ← PDF reports
│   └── search_report_*.docx            ← Word reports
│
├── test_phase1.py                      ← Phase 1: Config, Logger, imports, PyMuPDF
├── test_phase2.py                      ← Phase 2: WebSearchAgent search + result structure
├── test_phase3.py                      ← Phase 3: All agents + orchestrator integration
│
├── .env.example                        ← Environment variable template
├── .env                                ← Local environment config (gitignored)
├── requirements.txt                    ← Python dependencies
└── README.md
```

### Module Responsibilities

| Module | Responsibility | Dependencies |
|---|---|---|
| `orchestrator.py` | Pipeline lifecycle, stage sequencing, error handling | All agents, Config, Logger |
| `web_search_agent.py` | Web research via DuckDuckGo, optional AI summary | `requests`, `beautifulsoup4`, `openai` |
| `compliance_guard_agent.py` | Content validation, quality gate | Logger only (no external deps) |
| `document_formatter.py` | Multi-format document generation | `PyMuPDF`, `python-docx`, Config |
| `emailer_agent.py` | Email delivery with attachments | `smtplib` (stdlib), Config |
| `config.py` | Environment variable management | `python-dotenv` |
| `logger.py` | Singleton structured logging | `logging` (stdlib) |

---

## Testing

### Phase 1 — Core Utilities

Tests imports, environment variables, output directory, Logger singleton, Config validation, and PyMuPDF.

```bash
python test_phase1.py
```

**8 tests:**
1. Import `Config` and `Logger`
2. Load all environment variables
3. Verify `OUTPUT_DIR` exists and is writable
4. Logger singleton behaviour
5. `Config.validate()` returns empty list
6. Logger methods (`log_agent_activity`, `log_error`)
7. Virtual environment detection
8. PyMuPDF import (`import fitz` or `import pymupdf as fitz`)

### Phase 2 — Web Search Agent

Tests `WebSearchAgent` initialization, search execution, result structure, AI summary, and error handling.

```bash
python test_phase2.py
```

**7 tests:**
1. Import `WebSearchAgent`
2. Agent initialization (with/without Azure OpenAI)
3. Live search execution against DuckDuckGo
4. Result structure validation (required fields, types, source)
5. AI summary generation (or graceful skip)
6. Error handling (empty query)
7. Sample output display

### Phase 3 — Full Pipeline Integration

Tests all agents and the orchestrator end-to-end.

```bash
python test_phase3.py
```

**6 tests:**
1. All imports (agents + orchestrator)
2. Config validation
3. `ComplianceGuardAgent` with good and bad data
4. `DocumentFormatterAgent` file generation
5. `EmailerAgent` error handling (invalid email)
6. `PipelineOrchestrator` full pipeline execution

### Run All Tests

```bash
python test_phase1.py && python test_phase2.py && python test_phase3.py
```

---

## Troubleshooting

| Symptom | Cause | Resolution |
|---|---|---|
| `ModuleNotFoundError: dotenv` | Missing dependency | `pip install python-dotenv` |
| `ModuleNotFoundError: fitz` | PyMuPDF version issue | `pip install PyMuPDF` — use `import pymupdf as fitz` for v1.24+ |
| `ModuleNotFoundError: docx` | Missing dependency | `pip install python-docx` (not `docx`) |
| Config validation fails | Missing `.env` file | `cp .env.example .env` and fill in values |
| Web search returns 0 results | DuckDuckGo rate limiting | Wait 30s and retry; reduce `num_results` |
| AI summary is `None` | Azure OpenAI not configured | Expected behaviour — set env vars to enable |
| Email fails with auth error | Wrong SMTP credentials | Use app-specific password for Office 365/Gmail |
| Email fails with TLS error | Port mismatch | Use port 587 for STARTTLS, 465 for SSL |
| PDF generation fails | PyMuPDF not installed | `pip install PyMuPDF` — PDF stage is skipped gracefully |
| DOCX generation fails | python-docx not installed | `pip install python-docx` — DOCX stage is skipped gracefully |
| `Permission denied: outputs/` | Directory not writable | `chmod 755 outputs/` or check `OUTPUT_DIR` in `.env` |
| Pipeline status: `rejected` | Compliance gate triggered | Check `issues` field — improve query or increase result count |

---

## Azure Production Mapping

| Component | Local (this repo) | Azure Equivalent |
|---|---|---|
| Web search | DuckDuckGo HTML scraping | Azure Bing Search API |
| AI summary | Azure OpenAI GPT-4 (optional) | Azure OpenAI GPT-4o |
| Compliance validation | In-process Python rules | Azure Content Safety + custom policy |
| Document storage | Local `./outputs/` directory | Azure Blob Storage |
| PDF generation | PyMuPDF (local) | Azure Functions + PyMuPDF |
| Email delivery | SMTP/TLS (Office 365) | Azure Communication Services Email |
| Pipeline orchestration | `PipelineOrchestrator` | Azure Durable Functions |
| Configuration | `.env` file | Azure Key Vault + App Configuration |
| Logging | Python `logging` singleton | Azure Application Insights |
| Pipeline tracking | UUID in-process | Azure Cosmos DB (audit trail) |

---

## Production Checklist

| # | Item | Status |
|---|---|---|
| 1 | Environment variables validated at startup | ✅ |
| 2 | Pipeline UUID for every execution | ✅ |
| 3 | Compliance gate blocks unvalidated content | ✅ |
| 4 | Email only sends compliance-approved content | ✅ |
| 5 | Graceful degradation without Azure OpenAI | ✅ |
| 6 | Graceful degradation without PDF/DOCX libraries | ✅ |
| 7 | Singleton logger prevents log duplication | ✅ |
| 8 | SMTP credentials in `.env` (not hardcoded) | ✅ |
| 9 | Output directory created on demand | ✅ |
| 10 | Phase-based test coverage | ✅ |
| 11 | Error propagation stops pipeline on failure | ✅ |
| 12 | File existence check before email attachment | ✅ |

---

*Multi-Agentic AI · Production Research Pipeline · Maneesh Kumar*