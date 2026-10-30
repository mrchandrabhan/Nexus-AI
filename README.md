# Nexus AI — Enterprise Intelligence & Automation Platform

> **Status: Document-ingestion API implemented and committed; local rebuild and end-to-end verification pending. Semantic retrieval and answer generation are the next milestones.**

[![CI](https://github.com/mrchandrabhan/Nexus-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/mrchandrabhan/Nexus-AI/actions/workflows/ci.yml)

Nexus AI is a portfolio project exploring how an enterprise AI assistant can move beyond chat and safely help people work with organizational knowledge and business systems. The first working slice accepts knowledge documents, extracts text, creates traceable chunks, and persists document metadata and content in PostgreSQL. Embeddings, semantic retrieval, and cited answer generation are being built next.

**Repository:** https://github.com/mrchandrabhan/Nexus-AI  
**Portfolio:** https://mrchandrabhan.github.io/

## Current implementation

| Capability | Status |
|---|---|
| Project definition, architecture, and roadmap | Published |
| Next.js workspace shell | Implemented |
| FastAPI service, health, and readiness checks | Implemented |
| PostgreSQL document schema and Alembic migration | Implemented |
| PDF, Markdown, and UTF-8 text upload | Implemented |
| PDF text extraction with page metadata | Implemented |
| Overlapping text chunks with source offsets | Implemented |
| Document listing, detail, duplicate detection, and deletion | Implemented |
| Embedding generation and pgvector similarity search | Next milestone |
| Grounded LLM answers with citations | Planned |
| Authentication, tenant isolation, and RBAC | Planned |
| Approved tools and audit workflow | Planned |

The current upload API is a single-workspace development feature. Authentication and tenant-level authorization are not implemented yet; do not expose this development service to untrusted networks.

## Architecture

The current document flow is: user → Next.js workspace → FastAPI → document validation and extraction → overlapping chunks with page and offset metadata → PostgreSQL. The next milestone adds embeddings in pgvector, semantic retrieval, and source-cited model responses.

See docs/architecture.md for trust boundaries and design decisions.

## Technology

| Area | Technology | Purpose |
|---|---|---|
| Web | Next.js, TypeScript | Workspace UI |
| API | Python, FastAPI | Typed application API |
| Data | PostgreSQL, SQLAlchemy | Document metadata and extracted chunks |
| Migrations | Alembic | Versioned database schema |
| File parsing | pypdf | Text extraction from PDFs |
| Retrieval foundation | pgvector extension | Vector storage in the next milestone |
| Tests | pytest, FastAPI TestClient | API and ingestion coverage |
| Local environment | Docker Compose | Reproducible development |
| Delivery | GitHub Actions | Test and build automation |

## Document ingestion API

The API accepts PDF, Markdown, and UTF-8 TXT files up to 10 MiB. It stores extracted text chunks and document metadata, not the original binary file. PDF chunks retain page numbers; all chunks retain character offsets within their source page.

Open http://localhost:8000/docs and use these endpoints:

- POST /api/v1/documents — upload a file using multipart form data.
- GET /api/v1/documents — list uploaded document metadata.
- GET /api/v1/documents/{document_id} — inspect a document and its extracted chunks.
- DELETE /api/v1/documents/{document_id} — delete a document and its chunks.

Exact duplicate files are rejected by SHA-256 digest. Unsupported file types, empty files, invalid PDFs, encrypted PDFs, and files above the upload limit receive explicit errors. Scanned PDFs are not OCR-processed.

## Run locally

Prerequisites: Docker Desktop with the Linux container engine running, and Git.

From the repository root, run:

    docker compose up --build -d
    docker compose ps

Open:
- Web application: http://localhost:3000
- API documentation: http://localhost:8000/docs
- API liveness: http://localhost:8000/health
- API/database readiness: http://localhost:8000/ready

PostgreSQL is exposed on host port 5433. The pgvector extension is enabled for the next retrieval milestone. Alembic applies the document schema automatically when the backend container starts.

Run backend tests:

    docker compose exec backend pytest -q

Follow backend logs:

    docker compose logs -f backend

Stop the stack:

    docker compose down

To remove the local database volume as well (destructive), use: docker compose down -v.

The Compose file uses disposable development credentials for a local portfolio environment. Do not reuse them outside local development. Never commit real secrets.

## Security and reliability principles

- Treat uploaded documents and retrieved content as untrusted input.
- Enforce authorization in the API and tool layer, not only in prompts.
- Use allowlisted tools with validated schemas and least-privilege credentials.
- Keep read operations separate from write operations.
- Require an explicit human approval step before write actions.
- Avoid logging secrets or unnecessary document contents.
- Add timeouts, request limits, and clear failure responses.
- Evaluate groundedness and citation correctness; do not assume fluent output is correct.

## Development roadmap

See docs/roadmap.md. Planned capabilities are not described as complete until implemented and tested.

## Portfolio context

This project complements Agentic RAG Document Q&A. The earlier project focuses on document question answering and retrieval evaluation; Nexus AI is intended to explore enterprise ingestion, authorization boundaries, enterprise application integrations, and human-approved workflows.

## License

No license has been selected yet. Until one is added, normal copyright restrictions apply; please do not assume the code is reusable under an open-source license.
