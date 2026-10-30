# Nexus AI — Delivery Roadmap

This roadmap separates the first demonstrable vertical slice from future production-hardening work. Checkboxes should only be marked after the feature exists and has been verified.

## Phase 0 — Project baseline
- [x] Public repository created
- [x] Project goals and scope documented
- [x] Initial architecture and trust boundaries documented
- [ ] Add application scaffold
- [ ] Add linting, formatting, and CI

## Phase 1 — Working RAG assistant
- [ ] FastAPI health endpoint and typed API structure
- [ ] Next.js chat shell
- [ ] PostgreSQL connection and migrations
- [ ] PDF/Markdown upload and parsing
- [ ] Chunking with document/page metadata
- [ ] Embedding generation and pgvector index
- [ ] Retrieval endpoint with tenant/workspace filter
- [ ] LLM response with citations
- [ ] 20–30 labeled evaluation questions

## Phase 2 — Enterprise integration
- [ ] Conversation persistence
- [ ] Authentication and workspace membership
- [ ] One read-only business tool with a strict schema
- [ ] Tool authorization enforced server-side
- [ ] Approval request model and approval UI
- [ ] Audit log for tool proposals and approved actions

## Phase 3 — Quality and operations
- [ ] Unit and integration tests
- [ ] Retrieval, citation, and answer-quality report
- [ ] Prompt-injection and cross-workspace access tests
- [ ] Structured logs and request IDs
- [ ] OpenTelemetry tracing
- [ ] Latency and token/cost tracking
- [ ] Docker Compose development environment
- [ ] CI build/test workflow
- [ ] Deployment and operator runbook

## Future enhancements
- [ ] Additional model providers and routing policy
- [ ] Hybrid lexical/vector retrieval and reranking
- [ ] Durable multi-step agent workflows
- [ ] Rate limiting and per-workspace budgets
- [ ] Advanced evaluation and regression gates
- [ ] Kubernetes and Terraform deployment after the app stabilizes

## Definition of MVP complete

A user can sign in, upload a document, ask a question, receive an answer with verifiable citations, and use one read-only business tool. Automated tests cover the main API and retrieval flow, and the app can be run through documented steps. Any write workflow remains behind explicit approval.
