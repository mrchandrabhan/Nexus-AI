import hashlib
import logging
from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, DocumentChunk
from app.schemas.documents import DocumentDetail, DocumentSummary
from app.services.document_ingestion import (
    MAX_DOCUMENT_BYTES,
    DocumentExtractionError,
    InvalidDocument,
    UnsupportedDocumentType,
    chunk_pages,
    extract_pages,
    safe_filename,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and index a knowledge document",
)
async def upload_document(
    file: UploadFile = File(..., description="PDF, Markdown, or UTF-8 text file"),
    db: Session = Depends(get_db),
) -> Document:
    if not file.filename:
        raise HTTPException(status_code=422, detail="A filename is required.")

    try:
        filename = safe_filename(file.filename)
    except InvalidDocument as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    raw_bytes = await file.read(MAX_DOCUMENT_BYTES + 1)
    if len(raw_bytes) > MAX_DOCUMENT_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Document exceeds the 10 MiB upload limit.",
        )

    try:
        pages = extract_pages(filename, raw_bytes)
    except UnsupportedDocumentType as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except InvalidDocument as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(status_code=422, detail="No text chunks could be created.")

    digest = hashlib.sha256(raw_bytes).hexdigest()
    existing = db.scalar(select(Document).where(Document.sha256 == digest))
    if existing:
        raise HTTPException(
            status_code=409,
            detail="This exact document has already been uploaded.",
        )

    extension = PurePosixPath(filename.lower()).suffix
    content_type = {
        ".pdf": "application/pdf",
        ".md": "text/markdown",
        ".txt": "text/plain",
    }[extension]
    character_count = sum(len(page_text) for _, page_text in pages)

    document = Document(
        filename=filename,
        content_type=content_type,
        sha256=digest,
        character_count=character_count,
        chunk_count=len(chunks),
    )
    db.add(document)

    try:
        db.flush()
        db.add_all(
            [DocumentChunk(document_id=document.id, **chunk) for chunk in chunks]
        )
        db.commit()
        db.refresh(document)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This document could not be stored because it already exists.",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while storing uploaded document.")
        raise HTTPException(
            status_code=503,
            detail="The document could not be stored. Check database availability.",
        ) from exc

    return document


@router.get("", response_model=list[DocumentSummary], summary="List indexed documents")
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    statement = select(Document).order_by(Document.created_at.desc())
    return list(db.scalars(statement).all())


@router.get(
    "/{document_id}",
    response_model=DocumentDetail,
    summary="Get document metadata and extracted chunks",
)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
) -> Document:
    document = db.scalar(select(Document).where(Document.id == document_id))
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document and its extracted chunks",
)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
) -> None:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    db.delete(document)
    db.commit()
