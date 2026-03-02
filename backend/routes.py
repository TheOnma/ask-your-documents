"""FastAPI routes for the document Q&A service."""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai.pipelines.rag import answer, ingest_pdf
from ai.retrieval.retriever import collection_count

logger = logging.getLogger(__name__)

app = FastAPI(title="Document Q&A", description="RAG-powered document question answering")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request / Response models ---

class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list[dict]
    context_found: bool


class IngestResponse(BaseModel):
    filename: str
    chunks_stored: int


class StatusResponse(BaseModel):
    status: str
    total_chunks: int


# --- Routes ---

@app.get("/health", response_model=StatusResponse)
def health():
    """Check service health and collection size."""
    return {"status": "ok", "total_chunks": collection_count()}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile):
    """Upload and ingest a PDF document."""
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    tmp_path = Path(f"/tmp/{file.filename}")
    try:
        content = await file.read()
        tmp_path.write_bytes(content)
        chunks_stored = ingest_pdf(tmp_path)
    except Exception as e:
        logger.error("Ingestion failed for %s: %s", file.filename, e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)

    return {"filename": file.filename, "chunks_stored": chunks_stored}


@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):
    """Answer a question using the ingested documents."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = answer(request.question)
    except Exception as e:
        logger.error("Answer generation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    return result
