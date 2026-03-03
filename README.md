# Ask Your Documents

A local RAG (Retrieval-Augmented Generation) application that lets you upload documents and ask questions about them. Answers are grounded in your documents and always cite their sources.

---

## Features

- **Multi-format upload** — ingest PDF, Word (.docx), and plain text (.txt) files
- **Hybrid retrieval** — combines dense vector search (OpenAI embeddings) with BM25 keyword search, merged via Reciprocal Rank Fusion (RRF)
- **HyDE** — generates a hypothetical answer before retrieval to improve semantic matching
- **Source citations** — every answer links back to the document and page it came from
- **React UI** — sidebar document manager, scrollable chat, drag-and-drop upload
- **CLI** — ingest and query documents entirely from the terminal
- **Persistent storage** — ChromaDB stores embeddings on disk so nothing is lost between restarts

---

## Tech Stack

| Layer | Choice |
|---|---|
| LLM | GPT-4o (OpenAI) |
| Embeddings | `text-embedding-3-small` (OpenAI) |
| Vector store | ChromaDB (local, persistent) |
| Keyword search | BM25 (rank-bm25) |
| API | FastAPI + uvicorn |
| Frontend | React 18 + Vite + Tailwind CSS |

---

## Project Structure

```
ask-your-documents/
├── ai/
│   ├── config.py              # Settings via pydantic-settings + .env
│   ├── ingestion/
│   │   ├── loader.py          # PDF, DOCX, TXT loaders
│   │   ├── chunker.py         # Recursive character splitter (512 / 64 overlap)
│   │   └── embedder.py        # OpenAI embeddings
│   ├── retrieval/
│   │   └── retriever.py       # ChromaDB + BM25 + RRF hybrid retrieval
│   └── pipelines/
│       └── rag.py             # End-to-end ingest and answer pipeline
├── backend/
│   └── routes.py              # FastAPI routes: /ingest, /ask, /documents
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Layout: header, sidebar, chat, footer
│   │   ├── api.js             # Fetch wrappers for all API endpoints
│   │   └── components/
│   │       ├── Sidebar.jsx    # Upload zone + document list
│   │       ├── Chat.jsx       # Message bubbles + typing indicator
│   │       └── InputBar.jsx   # Question input
│   └── package.json
├── evals/                     # Evaluation dataset and harness (RAGAS-ready)
├── tests/                     # Integration tests (pytest)
├── main.py                    # CLI entry point
└── requirements.txt
```

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- An OpenAI API key

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/TheOnma/ask-your-documents.git
cd ask-your-documents

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env             # or create .env manually
```

Add your key to `.env`:

```
OPENAI_API_KEY=sk-...
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running the App

Open two terminals:

**Terminal 1 — Backend**
```bash
source .venv/bin/activate
python main.py serve
# API running at http://localhost:8000
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm run dev
# UI running at http://localhost:5173
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Using the Web UI

1. **Upload a document** — drag and drop or click the upload zone in the left sidebar. Supported: PDF, DOCX, TXT.
2. **Ask a question** — type in the input bar and press Enter or click Ask →.
3. **Read the answer** — the AI responds using only your documents. Sources (filename + page) are shown below each answer.
4. **Remove a document** — click the ✕ button next to any document in the sidebar to delete it from the knowledge base.

---

## Using the CLI

```bash
# Ingest a single file
python main.py ingest path/to/document.pdf
python main.py ingest path/to/report.docx
python main.py ingest path/to/notes.txt

# Ingest an entire directory
python main.py ingest path/to/documents/

# Ask a question
python main.py ask "What are the key findings?"

# Ask and see the retrieved context chunks
python main.py ask "What are the key findings?" --show-context
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service status and total chunk count |
| `GET` | `/documents` | List all ingested document names |
| `DELETE` | `/documents/{filename}` | Remove a document and all its chunks |
| `POST` | `/ingest` | Upload and ingest a document (multipart/form-data) |
| `POST` | `/ask` | Answer a question (`{"question": "..."}`) |

Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## How It Works

```
Upload              ┌─────────────┐   chunk   ┌──────────┐   embed   ┌───────────┐
PDF/DOCX/TXT  ─────▶│   Loader    │──────────▶│  Chunker │──────────▶│ Embedder  │
                    └─────────────┘           └──────────┘           └─────┬─────┘
                                                                            │ store
                                                                     ┌──────▼─────┐
                                                                     │  ChromaDB  │
                                                                     └──────┬─────┘
                                                                            │
Query         ┌──────────┐  HyDE  ┌──────────┐ hybrid  ┌──────────┐       │
"What is...?" │ Question │───────▶│  Embed   │────────▶│ Retrieve │◀──────┘
              └──────────┘        └──────────┘         └─────┬────┘
                                                              │ top-k chunks
                                                       ┌──────▼──────┐
                                                       │  GPT-4o     │
                                                       │  (answer)   │
                                                       └─────────────┘
```

**Retrieval** uses Reciprocal Rank Fusion to merge dense cosine similarity results with BM25 keyword results. If the best match scores below the relevance threshold (0.3), the system returns "I don't have enough information" rather than hallucinating.
