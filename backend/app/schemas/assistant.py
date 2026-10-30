from pydantic import BaseModel, Field, field_validator


class AssistantAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def question_must_contain_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Question cannot be blank.")
        return normalized


class Citation(BaseModel):
    n: int
    source: str
    page: int
    score: float
    text: str


class AssistantAnswer(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    trace: list[str]
    latency_ms: float
    engine: str


class RAGDocumentUpload(BaseModel):
    filename: str
    sha256: str
    files: int
    pages: int
    chunks: int


class AssistantStatus(BaseModel):
    status: str
    engine: str
    embedding_model: str
    indexed_documents: int
