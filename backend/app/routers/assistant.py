from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.schemas.assistant import (
    AssistantAnswer,
    AssistantAskRequest,
    AssistantRetrievalDebug,
    AssistantRetrieveRequest,
    AssistantStatus,
    RAGDocumentUpload,
)
from app.services.rag_client import (
    RAGClient,
    RAGServiceError,
    RAGServiceUnavailable,
)

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def get_rag_client() -> RAGClient:
    return RAGClient()


def map_rag_error(exc: RAGServiceError) -> HTTPException:
    if isinstance(exc, RAGServiceUnavailable):
        return HTTPException(status_code=503, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


@router.get("/status", response_model=AssistantStatus)
async def assistant_status(
    client: RAGClient = Depends(get_rag_client),
) -> dict:
    try:
        return await client.health()
    except RAGServiceError as exc:
        raise map_rag_error(exc) from exc


@router.post("/ask", response_model=AssistantAnswer)
async def ask(
    request: AssistantAskRequest,
    client: RAGClient = Depends(get_rag_client),
) -> dict:
    try:
        return await client.ask(request.question)
    except RAGServiceError as exc:
        raise map_rag_error(exc) from exc


@router.post("/retrieve", response_model=AssistantRetrievalDebug)
async def retrieve(
    request: AssistantRetrieveRequest,
    client: RAGClient = Depends(get_rag_client),
) -> dict:
    try:
        return await client.retrieve(request.question, request.limit)
    except RAGServiceError as exc:
        raise map_rag_error(exc) from exc


@router.post("/documents", response_model=RAGDocumentUpload)
async def upload_document(
    file: UploadFile = File(...),
    client: RAGClient = Depends(get_rag_client),
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=422, detail="A filename is required.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Document exceeds the 10 MiB upload limit.",
        )
    try:
        return await client.upload(
            file.filename,
            content,
            file.content_type or "application/octet-stream",
        )
    except RAGServiceError as exc:
        raise map_rag_error(exc) from exc
