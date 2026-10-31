# Nexus AI — Architecture Notes

## Product boundary

Nexus AI is the enterprise workspace and governance/control plane. The existing `agentic-rag-docqa` repository is the knowledge engine. Nexus calls that engine over HTTP; document parsing, chunking, embeddings, vector search, LangGraph retrieval, answer generation, and citation validation remain implemented in one place.

## Current service boundaries

### Nexus workspace (Next.js)

- Provides the enterprise workspace shell.
- Uploads supported documents through the Nexus API.
- Submits natural-language questions.
- Displays grounded answers, page-level citations, latency, and agent trace.
- Does not directly call the RAG service from the browser.

### Nexus API (FastAPI)

- Exposes assistant status, document-upload proxy, and question/answer endpoints.
- Calls the RAG service server-side through a typed HTTP client.
- Applies timeout and upstream error handling.
- Is the intended enforcement point for future identity, workspace authorization, tool policy, approvals, and audit records.

### Existing Agentic RAG service

- Wraps the existing `DocQA` pipeline in `api.py`.
- Loads the example corpus when the process-local engine is initialized.
- Accepts document uploads and indexes them through the existing page-aware loaders, chunker, embedding model, and FAISS store.
- Uses the existing LangGraph retrieve-grade-rewrite-generate flow and citation validation.
- Supports the existing MiniLM semantic embedder and deterministic hash embedder for local/offline development.
- Rebuilds its vector index in process memory at startup; uploaded source files are persisted in a mounted directory and re-indexed after a restart.

## Request flows

### Ask a question

1. The browser submits a question to `POST /api/v1/assistant/ask` on Nexus.
2. Nexus validates the request and calls the RAG API server-side.
3. The RAG engine retrieves and grades document chunks, optionally rewrites a weak query, and generates an answer from relevant context.
4. The RAG engine validates citation indices and returns source/page metadata and the agent trace.
5. Nexus returns the answer and citations to the browser for display.

### Upload a document

1. The browser sends a multipart file to Nexus.
2. Nexus enforces its 10 MiB request limit.
3. Nexus forwards the file to the RAG service.
4. The RAG service validates type and size, writes the source file to the persistent upload volume, and indexes it through the existing RAG pipeline.
5. The response includes file/page/chunk counts.

## Current limitations and trust boundaries

- No user authentication, workspace identity, or tenant isolation exists yet.
- The local RAG API currently has no service token; Compose binds its host port to loopback and keeps backend-to-RAG traffic on the private Compose network.
- The vector index is process-local and rebuilt at startup; uploaded source files and model cache are durable Docker volumes.
- Nexus currently proxies question and upload requests; it does not claim that documents are access-controlled.
- All retrieved documents must be treated as untrusted input.
- The current UI must not be exposed as an enterprise multi-tenant service.

## Next control-plane architecture

1. Add identity and workspace membership.
2. Associate each document with an authorized workspace and extend the RAG adapter to filter retrieval by an authorized corpus/document scope.
3. Add a tool registry with strict input/output schemas.
4. Enforce tool authorization in Nexus server-side code, independent of model prompts.
5. Separate read-only tools from state-changing tools.
6. Store proposed actions as approval requests and require explicit, authorized human approval.
7. Record actor, requested tool, validated arguments, decision, approver, execution result, and timestamps in an append-only audit trail.

## Non-goals

Nexus will not rebuild the RAG embedding/retrieval engine. It will also not provide unrestricted SQL access, autonomous production write access, or prompt-only permission controls.
