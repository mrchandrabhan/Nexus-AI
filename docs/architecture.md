# Nexus AI — Architecture Notes

> Design baseline. Components described here are planned until implemented and tested.

## System context

Nexus AI is a web application for asking questions over a controlled knowledge base and invoking explicitly allowlisted business tools. It is not intended to be an unrestricted autonomous operator.

## Initial deployment shape

Start as a **modular monolith**: one FastAPI deployment with distinct modules for identity, conversations, document ingestion, retrieval, orchestration, tools, and audit events. This keeps the MVP debuggable while preserving boundaries that can later be extracted if measured scaling needs justify it.

## Request flow

1. The browser sends an authenticated request to the API.
2. The API checks the user's identity and access to the requested workspace.
3. The orchestration layer selects a retrieval or tool workflow.
4. Retrieval returns passages with document identifiers and page/section metadata.
5. The model receives only the relevant context and constrained tool definitions.
6. The response is validated and returned with source references.
7. Any state-changing request is converted into a proposal and waits for explicit approval.
8. An audit record captures the actor, requested action, approval, and outcome without storing secrets.

## Data boundaries

- Documents are scoped to a workspace or tenant.
- Retrieval must filter by the caller's authorized scope before context is sent to a model.
- Tool endpoints re-check authorization independently of the model's tool choice.
- SQL access is exposed through narrowly defined query functions, not arbitrary model-generated SQL.
- Credentials are held in environment/secret management, never in prompts or repository files.

## Key entities (initial proposal)

- User
- Workspace
- WorkspaceMembership
- Conversation
- Message
- Document
- DocumentChunk
- ToolExecution
- ApprovalRequest
- AuditEvent

## Quality attributes

| Attribute | Initial design response |
|---|---|
| Security | Server-side authorization, scoped retrieval, allowlisted tools |
| Safety | Read/write separation and human approval for mutations |
| Traceability | Request IDs, tool-call records, evaluation cases |
| Maintainability | Modular FastAPI application and typed schemas |
| Reliability | Timeouts, retries only for safe/idempotent operations, graceful provider errors |
| Evaluation | Labeled question set with retrieval and citation checks |

## Decisions to validate during implementation

- Choose a specific embedding model after measuring local/cloud cost and retrieval quality.
- Choose an LLM provider adapter based on availability, pricing, and structured-tool support.
- Introduce LangGraph only if the workflow requires durable multi-step state; avoid framework complexity for simple request/response paths.
- Use PostgreSQL transactions for conversation and approval state.
- Add caching only after observing repeated work or latency bottlenecks.
