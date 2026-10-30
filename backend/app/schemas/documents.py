from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    content_type: str
    character_count: int
    chunk_count: int
    created_at: datetime


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chunk_index: int
    content: str
    page_number: int | None
    start_char: int
    end_char: int


class DocumentDetail(DocumentSummary):
    chunks: list[DocumentChunkResponse]
