import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.assistant import get_rag_client


class FakeRAGClient:
    async def health(self):
        return {
            "status": "ready",
            "engine": "agentic-rag-docqa",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "answer_model": "extractive",
            "retrieval": "hybrid-vector-and-lexical",
            "indexed_documents": 3,
            "indexed_chunks": 18,
        }

    async def ask(self, question):
        return {
            "question": question,
            "answer": "The locker code expires after 48 hours [1].",
            "citations": [
                {
                    "n": 1,
                    "source": "pantry_locker_policy.md",
                    "page": 1,
                    "score": 0.88,
                    "text": "Locker codes expire after 48 hours.",
                }
            ],
            "trace": ["retrieve: 2 chunks", "grade: 1/2", "generate: extractive", "cite: 1 citations"],
            "latency_ms": 7.5,
            "engine": "agentic-rag-docqa",
        }

    async def retrieve(self, question, limit=8):
        return {
            "question": question,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "answer_model": "extractive",
            "results": [
                {
                    "rank": 1,
                    "source": "resume.pdf",
                    "page": 1,
                    "score": 0.031,
                    "text": "Cloud infrastructure with Azure, Terraform and Kubernetes.",
                }
            ][:limit],
        }

    async def upload(self, filename, content, content_type):
        return {
            "filename": filename,
            "sha256": "a" * 64,
            "files": 1,
            "pages": 1,
            "chunks": 2,
            "characters": 150,
        }


@pytest.fixture
def client():
    app.dependency_overrides[get_rag_client] = FakeRAGClient
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_assistant_ask_returns_rag_citations(client):
    response = client.post(
        "/api/v1/assistant/ask",
        json={"question": "When does the locker code expire?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "48 hours" in body["answer"]
    assert body["citations"][0]["source"] == "pantry_locker_policy.md"
    assert body["citations"][0]["page"] == 1


def test_assistant_rejects_blank_question(client):
    response = client.post("/api/v1/assistant/ask", json={"question": "   "})
    assert response.status_code == 422


def test_assistant_upload_proxies_file_to_rag_engine(client):
    response = client.post(
        "/api/v1/assistant/documents",
        files={"file": ("new-runbook.md", b"# Runbook\nRestart only with approval.", "text/markdown")},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "new-runbook.md"
    assert response.json()["chunks"] == 2
    assert response.json()["characters"] == 150


def test_assistant_status_includes_models_and_index_counts(client):
    response = client.get("/api/v1/assistant/status")
    assert response.status_code == 200
    assert response.json()["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert response.json()["indexed_chunks"] == 18


def test_assistant_retrieval_debug_returns_top_source_passages(client):
    response = client.post(
        "/api/v1/assistant/retrieve",
        json={"question": "Which cloud technologies are on my resume?", "limit": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["source"] == "resume.pdf"
    assert body["results"][0]["page"] == 1
