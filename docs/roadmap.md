# Nexus AI — Delivery Roadmap

Checkboxes are marked complete only when code exists and automated or end-to-end checks verify it.

## Phase 0 — Workspace baseline
- [x] Project goals and architecture documented
- [x] Next.js workspace shell
- [x] FastAPI backend and service health endpoints
- [x] Docker Compose development environment
- [x] GitHub Actions backend/frontend/Compose checks

## Phase 1 — Reuse existing RAG engine
- [x] Add HTTP API adapter to the existing Agentic RAG project
- [x] Expose RAG readiness, document upload, document list, and ask endpoints
- [x] Add adapter tests with a fake engine (no model download in CI)
- [x] Add a typed server-side Nexus RAG client
- [x] Add Nexus assistant status, upload proxy, and ask endpoints
- [x] Add workspace UI for uploads, questions, citations, retrieval diagnostics, and agent trace
- [x] Run the RAG API as a health-gated Docker Compose service
- [x] Persist uploaded source files and re-index them on service startup
- [ ] Verify local end-to-end upload and question flow across both services

## Phase 2 — Enterprise identity and access
- [ ] Add user identity and workspace membership
- [ ] Add RBAC roles and server-side authorization checks
- [ ] Add workspace/document ownership and retrieval-scope filtering
- [ ] Authenticate Nexus-to-RAG service calls
- [ ] Add cross-workspace retrieval isolation tests

## Phase 3 — Controlled enterprise tools
- [ ] Define tool registry and strict tool schemas
- [ ] Add one read-only tool (service health or incident lookup)
- [ ] Enforce tool authorization in server-side policy code
- [ ] Add a state-changing tool proposal flow
- [ ] Add expiring, one-use human approval tokens
- [ ] Record approval and execution events in an audit log

## Phase 4 — Quality and operations
- [ ] Add prompt-injection and unauthorized-action tests
- [ ] Add structured logs and request IDs
- [ ] Add OpenTelemetry tracing and request latency metrics
- [ ] Add RAG regression and citation-validity gates to Nexus integration CI
- [ ] Add operator runbook and deployment hardening

## Product completion target

A user can sign in, ask questions against knowledge they are authorized to access, inspect source citations, use a read-only enterprise tool, and propose a state-changing action that requires an authorized human approval. Every sensitive action is auditable.
