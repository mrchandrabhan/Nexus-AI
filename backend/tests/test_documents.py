def test_upload_markdown_persists_document_and_chunks(client):
    markdown = (
        "# Incident response\n\n"
        "The on-call engineer acknowledges a production incident within five minutes.\n"
        "The incident commander records impact, assigns an owner, and posts updates."
    )

    response = client.post(
        "/api/v1/documents",
        files={"file": ("incident-runbook.md", markdown.encode(), "text/markdown")},
    )

    assert response.status_code == 201
    document = response.json()
    assert document["filename"] == "incident-runbook.md"
    assert document["content_type"] == "text/markdown"
    assert document["character_count"] == len(markdown)
    assert document["chunk_count"] >= 1

    detail = client.get("/api/v1/documents/" + document["id"])
    assert detail.status_code == 200
    assert "acknowledges a production incident" in detail.json()["chunks"][0]["content"]
    assert detail.json()["chunks"][0]["page_number"] == 1

    listing = client.get("/api/v1/documents")
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_duplicate_document_is_rejected(client):
    content = b"Do not page the database team for a frontend-only alert."
    first = client.post(
        "/api/v1/documents",
        files={"file": ("runbook.txt", content, "text/plain")},
    )
    second = client.post(
        "/api/v1/documents",
        files={"file": ("another-name.txt", content, "text/plain")},
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_unsupported_file_type_is_rejected(client):
    response = client.post(
        "/api/v1/documents",
        files={"file": ("notes.docx", b"not supported", "application/octet-stream")},
    )
    assert response.status_code == 415


def test_empty_text_file_is_rejected(client):
    response = client.post(
        "/api/v1/documents",
        files={"file": ("empty.txt", b"   ", "text/plain")},
    )
    assert response.status_code == 422


def test_invalid_pdf_is_rejected(client):
    response = client.post(
        "/api/v1/documents",
        files={"file": ("broken.pdf", b"not a pdf", "application/pdf")},
    )
    assert response.status_code == 422


def test_delete_document_removes_it(client):
    created = client.post(
        "/api/v1/documents",
        files={"file": ("delete-me.txt", b"Temporary knowledge.", "text/plain")},
    )
    document_id = created.json()["id"]

    deleted = client.delete("/api/v1/documents/" + document_id)
    missing = client.get("/api/v1/documents/" + document_id)

    assert deleted.status_code == 204
    assert missing.status_code == 404
