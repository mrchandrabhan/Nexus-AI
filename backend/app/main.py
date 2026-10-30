import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.routers.documents import router as documents_router

app = FastAPI(
    title="Nexus AI API",
    description=(
        "Enterprise knowledge workspace API. The current slice supports document "
        "ingestion and extraction; semantic retrieval and answer generation are next."
    ),
    version="0.2.0",
)

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(documents_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"service": "nexus-ai-api", "version": "0.2.0", "docs": "/docs"}


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Liveness check: confirms the API process can answer requests."""
    return {"status": "ok", "service": "nexus-ai-api"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    """Readiness check: confirms the API can reach PostgreSQL."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready", "database": "connected"}
