# Aperture RAG Q&A Assistant

A modular, production-ready Retrieval-Augmented Generation (RAG) assistant designed to answer user queries using **only** product documentation for **Aperture** (from `ai-engineer-take-home/sample_corpus/`).

Built with **Google Gemini Flash** (`gemini-1.5-flash` / `gemini-2.0-flash`) and `text-embedding-004`.

---

## Folder Structure

The repository is structured into distinct, decoupled components as requested:

```
d:\Projrct\RAG_PIPLINE_PRINTDEED\
├── project/
│   ├── ingestion/             # Document loading & markdown header-aware chunking
│   │   ├── document_loader.py
│   │   └── chunker.py
│   ├── database/              # SQLite + NumPy vector store
│   │   └── vector_store.py
│   ├── retrieval/              # Query embedding, vector retrieval & Gemini answer generator
│   │   ├── retriever.py
│   │   ├── generator.py
│   │   └── pipeline.py
│   ├── ui/                     # FastAPI backend & dynamic Web UI
│   │   ├── app.py
│   │   └── index.html
│   └── tests/                  # Pytest test suite
│       ├── test_chunker.py
│       ├── test_retrieval.py
│       └── test_pipeline.py
├── qa.py                       # Top-level CLI entry point
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## Quickstart

### 1. Installation

Install required dependencies:

```bash
pip install -r project/requirements.txt
```

### 2. Environment Setup (Google Gemini API Key)

You can provide your Google Gemini API key via a `.env` file or environment variables:

#### Option A: Using `.env` File (Recommended)
Copy `.env.example` to `.env` and fill in your Gemini API key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

#### Option B: Environment Variable
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"

# Linux / macOS / Bash
export GEMINI_API_KEY="your_api_key_here"
```

> **Note:** If `GEMINI_API_KEY` is not set in `.env` or system env, the pipeline automatically runs in `--mock` mode with a deterministic stub.


---

## How to Run

### Command-Line Interface (CLI)

Run `qa.py` directly with your question:

```bash
# Live API mode
python qa.py "How do I reset my Aperture API key?"

# Offline Mock mode (no API key required)
python qa.py "How do I reset my Aperture API key?" --mock
```

#### Example Output

```text
============================================================
QUESTION: How do I reset my Aperture API key?
============================================================

ANSWER:
To reset your Aperture API key, there is no remote reset endpoint. An owner or admin must go to Workspace Settings > API Keys in the dashboard and click 'Revoke', then generate a new one. Revoking takes effect within 60 seconds.

CITATIONS:
 - api-reference.md
============================================================
```

### Web UI

Launch the Web UI backend:

```bash
python project/ui/app.py
```

Then open your browser at `http://127.0.0.1:8000` to interact with the visual interface!

---

## Running Automated Tests

Run the test suite with `pytest`:

```bash
python -m pytest project/tests/
```

This verifies:
1. Document loading & header-aware chunking.
2. Vector storage & cosine similarity retrieval.
3. Citation tracking.
4. **Mandatory Refusal Fallback** on out-of-scope queries (e.g. asking for annual contract refund policy).

---

## Core Architecture & Mechanics

1. **Chunking Strategy (`project/ingestion/chunker.py`)**:
   - Header-aware Markdown chunking. Splits text at `#`, `##`, `###` headings to keep semantic sections intact while embedding document filename and heading tags into chunk headers (`[api-reference.md > Resetting an API key]`).

2. **Embeddings & Vector Store (`project/database/vector_store.py` & `project/retrieval/retriever.py`)**:
   - Generates 768-dim embeddings via Google Gemini `text-embedding-004`.
   - Stores chunks and vectors in a local SQLite database (`vector_store.db`) with normalized NumPy matrix operations for ultra-fast cosine similarity search.

3. **Grounded Generation & Citation (`project/retrieval/generator.py`)**:
   - Uses `gemini-1.5-flash` with system prompts enforcing strict grounding: the model is restricted to facts explicitly in context chunks and must cite exact source documents.

4. **"I Don't Know" / Refusal Handling**:
   - Primary defense against hallucination: If retrieved chunks do not meet relevance thresholds or do not contain facts needed to answer the question, the system returns a standardized refusal message:
     `"I do not have enough information in the provided documentation to answer your question."`

---

## Trade-offs & Future Extensions

- **Vector Storage**: Used SQLite + NumPy cosine similarity instead of an external vector DB service (like Pinecone/Weaviate) to minimize external setup dependencies and keep execution 100% self-contained.
- **Future Improvements**:
  - Add version-aware temporal conflict resolution for changelogs.
  - Implement hybrid search (BM25 keyword search + Dense Vector search) for enhanced retrieval precision.
