import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List

from dotenv import load_dotenv
from project.retrieval.pipeline import RAGPipeline

# Load API keys from .env file
load_dotenv()

app = FastAPI(title="Aperture RAG Q&A Assistant", version="1.0.0")

# Initialize pipeline
pipeline = RAGPipeline()


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    mock: Optional[bool] = False


@app.on_event("startup")
def startup_event():
    """Ensure documents are indexed on startup."""
    pipeline.ingest()


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serves the main web UI page."""
    html_file = Path(__file__).parent / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding="utf-8")
    return "<h1>Aperture RAG Assistant UI</h1>"


@app.post("/api/query")
def process_query(req: QueryRequest):
    """Processes a user question through the RAG pipeline."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    # Configure pipeline mock mode if requested
    if req.mock:
        pipeline.mock = True
        pipeline.retriever.mock = True
        pipeline.generator.mock = True
    else:
        # Auto-detect if GEMINI_API_KEY or GOOGLE_API_KEY is present
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            pipeline.mock = True
            pipeline.retriever.mock = True
            pipeline.generator.mock = True

    result = pipeline.answer_question(req.query, top_k=req.top_k)
    return result


@app.post("/api/reindex")
def reindex_corpus():
    """Forces re-indexing of the sample corpus."""
    count = pipeline.ingest(force_reindex=True)
    return {"message": "Re-indexing complete", "chunks_indexed": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
