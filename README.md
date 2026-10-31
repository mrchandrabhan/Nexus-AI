# Nexus AI — Enterprise AI Intelligence & Governance Platform

> **Status: Local-first MVP. Docker Compose runs the Next.js workspace, FastAPI control plane, PostgreSQL, and the shared Agentic RAG service. Document uploads persist in a named volume and are re-indexed after restarts. Identity, RBAC, policy enforcement, approvals, and audit logging remain future milestones.**

[![CI](https://github.com/mrchandrabhan/Nexus-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/mrchandrabhan/Nexus-AI/actions/workflows/ci.yml)

Nexus AI is the enterprise workspace and governance layer for the separate [Agentic RAG Document Q&A](https://github.com/mrchandrabhan/agentic-rag-docqa) project. It reuses that existing system for document loading, chunking, local MiniLM embeddings, hybrid vector/lexical retrieval, LangGraph orchestration, deterministic extractive answers, abstention, and page-level citations. No hosted LLM API is required. Nexus focuses on the capabilities around the knowledge engine: workspace UX, server-side integration, identity, authorization, controlled tools, human approvals, and audit history.

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
  ├── citation validation and abstention
  └── disk-backed uploads re-indexed at startup
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
| Docker Compose-managed RAG API with health-gated startup | Implemented |
| Persistent upload and local model-cache volumes | Implemented |
| Local extractive answers with source citations | Reused from existing project |
| RAG engine document parsing, embeddings, hybrid retrieval, and LangGraph | Reused from existing project |
| Authentication and workspace membership | Next milestone |
| RBAC and retrieval-scope enforcement | Next milestone |
| Controlled tool registry and policy engine | Planned |
| Human approval and audit workflow | Planned |

The vector index is rebuilt in memory at RAG service startup. Uploaded source files, model files, and query logs are stored in Docker named volumes; saved uploads are re-indexed after a restart. The stack binds its development ports to loopback. This remains a local demonstration, not a multi-tenant production deployment.

## Run locally

Clone the two repositories side by side so the Compose build can use the shared RAG engine:

```text
Projects/Portfolio/
  nexus-ai/
  agentic-rag-docqa/
```

From PowerShell, update both repositories and start the complete stack:

```powershell
cd "$HOME\Projects\Portfolio\agentic-rag-docqa"
git pull origin main

cd "$HOME\Projects\Portfolio\nexus-ai"
git pull origin main
docker compose up --build -d
docker compose ps
```

Docker Compose starts PostgreSQL, the local MiniLM-backed RAG API, the Nexus FastAPI backend, and the Next.js workspace. The first RAG startup downloads MiniLM into a named model-cache volume; later startups reuse the cached model.

Open:
- Nexus workspace: http://localhost:3000
- Nexus API docs: http://localhost:8000/docs
- Nexus API readiness: http://localhost:8000/ready
- RAG API docs: http://localhost:7861/docs
- RAG readiness: http://localhost:7861/ready

The RAG API binds to `127.0.0.1` on the host and is called by the backend over the private Compose network. Uploaded source files are kept in the `rag_uploads` volume and re-indexed after a container restart. The vector index itself is rebuilt in memory. No external LLM API key or hosted inference service is used.

### Try the workflow

1. Confirm Nexus API, database, and RAG service show Connected.
2. Upload a PDF, DOCX, TXT, or Markdown file from the Knowledge Base card.
3. Ask a question about the sample or uploaded documents.
4. Inspect the answer, source file, page number, retrieved passages, and agent execution trace.
5. Restart the RAG container with `docker compose restart rag`; the uploaded source should still be indexed when the service becomes healthy again.

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

This stops the services but preserves database, uploaded documents, model cache, and query-log volumes. Use `docker compose down -v` only when you intentionally want to delete all local persisted data.

## License

No license has been selected yet. Until one is added, normal copyright restrictions apply; please do not assume the code is reusable under an open-source license.
