from io import BytesIO
from pathlib import PurePosixPath
from typing import Iterable

from pypdf import PdfReader


MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


class UnsupportedDocumentType(ValueError):
    pass


class InvalidDocument(ValueError):
    pass


class DocumentExtractionError(ValueError):
    pass


def safe_filename(filename: str) -> str:
    normalized = filename.replace("\\", "/")
    name = PurePosixPath(normalized).name.strip()
    if not name or name in {".", ".."}:
        raise InvalidDocument("A valid filename is required.")
    if len(name) > 255:
        raise InvalidDocument("Filename must be 255 characters or fewer.")
    return name


def extract_pages(filename: str, raw_bytes: bytes) -> list[tuple[int, str]]:
    extension = PurePosixPath(filename.lower()).suffix

    if extension not in {".txt", ".md", ".pdf"}:
        raise UnsupportedDocumentType("Only PDF, Markdown, and TXT files are supported.")

    if not raw_bytes:
        raise InvalidDocument("The uploaded file is empty.")

    if extension in {".txt", ".md"}:
        try:
            text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise InvalidDocument("Text files must use UTF-8 encoding.") from exc

        text = text.replace(chr(0), "").strip()
        if not text:
            raise InvalidDocument("No readable text was found in the uploaded file.")
        return [(1, text)]

    if b"%PDF-" not in raw_bytes[:1024]:
        raise InvalidDocument("The uploaded file does not appear to be a valid PDF.")

    try:
        reader = PdfReader(BytesIO(raw_bytes), strict=False)
        if reader.is_encrypted:
            raise InvalidDocument("Password-protected PDFs are not supported.")
        pages: list[tuple[int, str]] = []
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or "").strip()
            if page_text:
                pages.append((page_number, page_text))
    except InvalidDocument:
        raise
    except Exception as exc:
        raise DocumentExtractionError("The PDF could not be parsed.") from exc

    if not pages:
        raise InvalidDocument(
            "No extractable text was found. Scanned PDFs require OCR, which is not enabled."
        )
    return pages


def chunk_pages(
    pages: Iterable[tuple[int, str]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, int | str | None]]:
    if chunk_size < 100:
        raise ValueError("chunk_size must be at least 100 characters.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size - 1.")

    chunks: list[dict[str, int | str | None]] = []
    for page_number, page_text in pages:
        page_text = page_text.strip()
        start = 0
        while start < len(page_text):
            end = min(start + chunk_size, len(page_text))
            if end < len(page_text):
                search_from = start + int(chunk_size * 0.65)
                boundary = page_text.rfind(chr(10), search_from, end)
                if boundary == -1:
                    boundary = page_text.rfind(" ", search_from, end)
                if boundary > start:
                    end = boundary

            segment = page_text[start:end]
            leading = len(segment) - len(segment.lstrip())
            trailing_end = len(segment.rstrip())
            content = segment.strip()
            if content:
                chunks.append(
                    {
                        "chunk_index": len(chunks),
                        "content": content,
                        "page_number": page_number,
                        "start_char": start + leading,
                        "end_char": start + trailing_end,
                    }
                )

            if end >= len(page_text):
                break
            start = max(start + 1, end - overlap)

    return chunks
