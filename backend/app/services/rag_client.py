import os
from typing import Any

import httpx


class RAGServiceError(RuntimeError):
    pass


class RAGServiceUnavailable(RAGServiceError):
    pass


class RAGClient:
    """Server-side HTTP adapter for the separately hosted Agentic RAG service."""

    def __init__(self, base_url: str | None = None, timeout: float = 45.0) -> None:
        self.base_url = (base_url or os.getenv(
            "RAG_API_BASE_URL", "http://host.docker.internal:7861"
        )).rstrip("/")
        self.timeout = timeout

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                trust_env=False,
            ) as client:
                response = await client.request(
                    method, f"{self.base_url}{path}", **kwargs
                )
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
            raise RAGServiceUnavailable(
                "The RAG service is unavailable. Start the agentic-rag-docqa API."
            ) from exc
        except httpx.HTTPError as exc:
            raise RAGServiceUnavailable("Could not communicate with the RAG service.") from exc

        if response.status_code >= 500:
            raise RAGServiceUnavailable("The RAG service returned an internal error.")
        if response.is_error:
            try:
                detail = response.json().get("detail", "RAG request was rejected.")
            except ValueError:
                detail = "RAG request was rejected."
            raise RAGServiceError(str(detail))

        try:
            return response.json()
        except ValueError as exc:
            raise RAGServiceUnavailable("The RAG service returned an invalid response.") from exc

    async def health(self) -> dict[str, Any]:
        return await self._request("GET", "/ready")

    async def ask(self, question: str) -> dict[str, Any]:
        return await self._request(
            "POST", "/api/v1/ask", json={"question": question}
        )

    async def retrieve(self, question: str, limit: int = 8) -> dict[str, Any]:
        return await self._request(
            "POST", "/api/v1/retrieve",
            json={"question": question, "limit": limit},
        )

    async def upload(self, filename: str, content: bytes, content_type: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/api/v1/documents",
            files={"file": (filename, content, content_type)},
        )
