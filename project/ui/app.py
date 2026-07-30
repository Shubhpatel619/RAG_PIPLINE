import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from project.retrieval.pipeline import RAGPipeline

load_dotenv()

app = FastAPI(title="Aperture LangChain RAG Q&A Assistant", version="2.0.0")


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Initialize RAG Pipeline
pipeline = None


def get_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = RAGPipeline()
    return pipeline


@app.on_event("startup")
def startup_event():
    """Ensure documents are indexed on startup."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        get_pipeline().ingest()


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serves the main web UI page."""
    html_file = Path(__file__).parent / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding="utf-8")
    return "<h1>Aperture RAG Assistant UI</h1>"


@app.post("/api/query")
def process_query(req: QueryRequest):
    """Processes a user question through the LangChain RAG pipeline."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="GEMINI_API_KEY is missing. Please set GEMINI_API_KEY in your .env file or environment."
        )

    result = get_pipeline().answer_question(req.query, top_k=req.top_k)
    return result


@app.post("/api/reindex")
def reindex_corpus():
    """Forces re-indexing of the sample corpus into FAISS."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="GEMINI_API_KEY is missing. Please set GEMINI_API_KEY in your .env file or environment."
        )

    count = get_pipeline().ingest(force_reindex=True)
    return {"message": "Re-indexing complete", "chunks_indexed": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
