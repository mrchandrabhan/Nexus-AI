# Nexus AI — Architecture Notes

## Current implementation boundary

The application currently implements a single-workspace document-ingestion API. It accepts PDF, Markdown, and UTF-8 text files, extracts text, creates overlapping chunks with source offsets, and persists metadata and chunks in PostgreSQL. Alembic owns the versioned schema. Authentication, tenant isolation, embeddings, semantic retrieval, and LLM responses are not implemented yet.

The current API is intended for local development and portfolio demonstration. It must not be exposed as a production multi-tenant service before identity, authorization, request controls, and isolation are added.

## Initial deployment shape

Start as a modular monolith: one FastAPI deployment with distinct modules for identity, conversations, document ingestion, retrieval, orchestration, tools, and audit events. This keeps the MVP debuggable while preserving boundaries that can later be extracted if measured scaling needs justify it.

## Implemented document flow

1. The browser or API client submits a PDF, Markdown, or UTF-8 TXT file.
2. The API validates extension, byte size, filename, and document readability.
3. PDF text is extracted page by page; text and Markdown are treated as page one.
4. Text is split into overlapping chunks, retaining page numbers and character offsets.
5. A SHA-256 digest prevents exact duplicate uploads.
6. Document metadata and extracted chunks are committed in one database transaction.
7. A caller can list documents, inspect extracted chunks, or delete a document and its chunks.

The original binary upload is not retained. Scanned PDFs are rejected because OCR is not part of the current implementation.

## Planned request flow

1. The browser sends an authenticated request to the API.
2. The API checks the user's identity and access to the requested workspace.
3. The orchestration layer selects a retrieval or tool workflow.
4. Retrieval returns passages with document identifiers and page/section metadata.
5. The model receives only the relevant context and constrained tool definitions.
6. The response is validated and returned with source references.
7. Any state-changing request is converted into a proposal and waits for explicit approval.
8. An audit record captures the actor, requested action, approval, and outcome without storing secrets.

## Data boundaries

- Documents are intended to be scoped to a workspace or tenant; tenant isolation is not implemented in this first slice.
- Retrieved content must be treated as untrusted input.
- Retrieval must filter by the caller's authorized scope before context is sent to a model.
- Tool endpoints must re-check authorization independently of the model's tool choice.
- SQL access must be exposed through narrowly defined query functions, not arbitrary model-generated SQL.
- Credentials belong in environment/secret management, never in prompts or repository files.

## Current data model

- Document
- DocumentChunk

## Planned data model

- User
- Workspace
- WorkspaceMembership
- Conversation
- Message
- ToolExecution
- ApprovalRequest
- AuditEvent

## Quality attributes

| Attribute | Initial design response |
|---|---|
| Security | Upload size/type validation; authorization and tenant isolation remain future work |
| Traceability | Document SHA-256, chunk index, page number, and source offsets |
| Maintainability | Modular FastAPI application and typed API schemas |
| Reliability | Database transactions, unique constraints, and explicit parsing errors |
| Evaluation | Unit and integration tests; retrieval evaluation is a future milestone |

## Decisions to validate during implementation

- Choose a specific embedding model after measuring local/cloud cost and retrieval quality.
- Choose an LLM provider adapter based on availability, pricing, and structured-tool support.
- Introduce LangGraph only if the workflow requires durable multi-step state; avoid framework complexity for simple request/response paths.
- Use PostgreSQL transactions for conversation and approval state.
- Add caching only after observing repeated work or latency bottlenecks.
