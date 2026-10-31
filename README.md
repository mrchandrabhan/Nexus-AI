# Nexus AI — Enterprise AI Intelligence & Governance Platform

> **Status: Existing Agentic RAG engine integrated through an HTTP adapter; Nexus chat and document upload UI implemented. Identity, RBAC, policy enforcement, approvals, and audit logging are the next build stages.**

[![CI](https://github.com/mrchandrabhan/Nexus-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/mrchandrabhan/Nexus-AI/actions/workflows/ci.yml)

Nexus AI is the enterprise workspace and governance layer for the separate [Agentic RAG Document Q&A](https://github.com/mrchandrabhan/agentic-rag-docqa) project. It reuses that existing system for document loading, chunking, embeddings, vector retrieval, LangGraph workflows, answer generation, abstention, and page-level citations. Nexus focuses on the capabilities around the knowledge engine: workspace UX, server-side integration, identity, authorization, controlled tools, human approvals, and audit history.

**Repository:** https://github.com/mrchandrabhan/Nexus-AI  
**Portfolio:** https://mrchandrabhan.github.io/

## Product architecture

```
Nexus Next.js workspace
  ├── document upload
  ├── question and answer UI
  └── source citations and agent trace
           |
           v
Nexus FastAPI control plane
  ├── server-side RAG service client
  ├── future identity and workspace authorization
  ├── future tool registry and policy engine
  ├── future approval workflow
  └── future audit events
           |
           v
Existing Agentic RAG HTTP adapter
  ├── page-aware document parsing and chunking
  ├── MiniLM or deterministic hash embeddings
  ├── FAISS / Chroma vector retrieval
  ├── LangGraph retrieve-grade-rewrite-generate flow
  └── citation validation and abstention
```

Nexus does not maintain a second embedding or retrieval pipeline. The existing RAG repository remains independently runnable and independently tested.

## Current implementation

| Capability | Status |
|---|---|
| Next.js enterprise workspace shell | Implemented |
| FastAPI control-plane API and health checks | Implemented |
| Server-side HTTP client for the existing RAG engine | Implemented |
| Nexus assistant question endpoint | Implemented |
| Nexus document-upload proxy | Implemented |
| Chat UI with grounded answer, citations, and agent trace | Implemented |
| RAG service status in the workspace | Implemented |
| RAG engine document parsing, embeddings, retrieval, and LangGraph | Reused from existing project |
| Authentication and workspace membership | Next milestone |
| RBAC and retrieval-scope enforcement | Next milestone |
| Controlled tool registry and policy engine | Planned |
| Human approval and audit workflow | Planned |

The current RAG adapter uses a process-local vector index. Sample documents are indexed at first initialization; uploads remain in memory and are cleared when that process restarts. This integration is for local development and demonstration, not a multi-tenant production deployment.

## Run locally

### 1. Start the existing RAG API

Open a PowerShell window in your existing `agentic-rag-docqa` clone:

```powershell
git pull origin main
pip install -r requirements.txt
$env:EMBEDDER = "minilm"
uvicorn api:app --host 0.0.0.0 --port 7861
```

The hash embedder is deterministic and quick for local integration tests. For semantic retrieval, use `$env:EMBEDDER = "minilm"` and allow the MiniLM model to download. Answer generation stays local: the RAG service selects relevant sentences from retrieved passages and includes source citations. No hosted language-model API or API key is used.

The adapter indexes the included incident, Kafka, and pantry sample documents when it initializes. Open http://localhost:7861/docs to inspect it.

### 2. Start Nexus

In a second PowerShell window:

```powershell
cd "$HOME\Projects\Portfolio\nexus-ai"
git pull origin main
docker compose up --build -d
docker compose ps
```

Open:
- Nexus workspace: http://localhost:3000
- Nexus API docs: http://localhost:8000/docs
- Nexus API liveness: http://localhost:8000/health
- Nexus database readiness: http://localhost:8000/ready

Docker Desktop connects the Nexus backend to the host's RAG API using `host.docker.internal:7861`.

### 3. Try the workflow

1. Confirm the RAG service status shows Connected in Nexus.
2. Upload a PDF, DOCX, TXT, or Markdown document from the Knowledge Base card.
3. Ask a question about the sample or uploaded documents.
4. Inspect the returned answer, source file, page number, and agent execution trace.

The RAG service is a separate process and must remain running while using Nexus.

## API endpoints

Nexus exposes:
- `GET /api/v1/assistant/status` — RAG engine status.
- `POST /api/v1/assistant/documents` — proxy a document upload to the RAG engine.
- `POST /api/v1/assistant/ask` — proxy a question and return the grounded answer and citations.
- `POST /api/v1/assistant/retrieve` — inspect top retrieved passages when debugging a question.

The existing RAG adapter exposes:
- `GET /health` and `GET /ready`
- `GET /api/v1/documents`
- `POST /api/v1/documents`
- `POST /api/v1/ask`

## Security boundaries and next work

The current workspace has no authentication or tenant isolation. The RAG adapter is intended to run on a trusted local development machine; it is not safe to expose publicly. Before production-style deployment, implement user identity, server-side workspace authorization, retrieval scoping, request limits, service authentication, and secret management.

Next, Nexus will become the enforcement point for tool calls. The model may propose an action, but the server-side policy layer must check user permissions and tool schemas independently. State-changing operations must wait for a human approval and produce an audit event. Prompts are not an authorization mechanism.

## Engineering roadmap

See [docs/roadmap.md](docs/roadmap.md) and [docs/architecture.md](docs/architecture.md). Only implemented and verified functionality is marked complete.

## Stop services

```powershell
docker compose down
```

Stop the RAG API with Ctrl+C in its terminal. Do not use `docker compose down -v` unless you intentionally want to delete the local PostgreSQL volume.

## License

No license has been selected yet. Until one is added, normal copyright restrictions apply; please do not assume the code is reusable under an open-source license.
