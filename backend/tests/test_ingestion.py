from app.services.document_ingestion import chunk_pages, safe_filename


def test_chunking_preserves_page_and_overlap():
    text = ("Operations teams review service health every morning. " * 40).strip()
    chunks = chunk_pages([(3, text)], chunk_size=500, overlap=100)

    assert len(chunks) > 1
    assert all(chunk["page_number"] == 3 for chunk in chunks)
    assert chunks[1]["start_char"] < chunks[0]["end_char"]
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_index"] == 1


def test_filename_is_reduced_to_basename():
    assert safe_filename("folder\\private\\runbook.md") == "runbook.md"
