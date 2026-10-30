# Nexus AI — Delivery Roadmap

Checkboxes should only be marked after the feature exists and has been verified.

## Phase 0 — Project baseline
- [x] Public repository created
- [x] Project goals and scope documented
- [x] Initial architecture and trust boundaries documented
- [x] Next.js and FastAPI application scaffold
- [x] Docker Compose development environment
- [x] API liveness/readiness endpoints and smoke tests
- [x] GitHub Actions test/build workflow

## Phase 1 — Working RAG assistant
- [x] PostgreSQL document schema and versioned Alembic migration
- [x] PDF, Markdown, and UTF-8 text upload endpoint
- [x] PDF text extraction with page metadata
- [x] Overlapping chunking with source character offsets
- [x] Persistent document and chunk metadata
- [x] Document list, detail, duplicate detection, and deletion endpoints
- [ ] Embedding generation with a measured embedding model
- [ ] pgvector storage and similarity index
- [ ] Retrieval endpoint with workspace authorization filter
- [ ] LLM response with verifiable source citations
- [ ] 20–30 labeled retrieval and answer evaluation questions
- [ ] Next.js upload and chat interface wired to the API

## Phase 2 — Enterprise integration
- [ ] Conversation persistence
- [ ] Authentication and workspace membership
- [ ] One read-only business tool with a strict schema
- [ ] Tool authorization enforced server-side
- [ ] Approval request model and approval UI
- [ ] Audit log for tool proposals and approved actions

## Phase 3 — Quality and operations
- [ ] Prompt-injection and cross-workspace access tests
- [ ] Structured logs and request IDs
- [ ] OpenTelemetry tracing
- [ ] Latency and token/cost tracking
- [ ] Retrieval, citation, and answer-quality regression report
- [ ] Deployment and operator runbook

## Future enhancements
- [ ] Additional model providers and routing policy
- [ ] Hybrid lexical/vector retrieval and reranking
- [ ] Durable multi-step agent workflows
- [ ] Rate limiting and per-workspace budgets
- [ ] Kubernetes and Terraform deployment after the app stabilizes

## Definition of MVP complete

A user can sign in, upload a document, ask a question, receive an answer with verifiable citations, and use one read-only business tool. Automated tests cover the main API and retrieval flow, and the app can be run through documented steps. Any write workflow remains behind explicit approval.
