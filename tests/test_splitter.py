from app.ingestion.splitter import split_text


def test_split_returns_chunks():
    text = "word " * 300
    chunks = split_text(text)
    assert len(chunks) > 1


def test_split_empty_text():
    chunks = split_text("")
    assert chunks == []


def test_split_short_text_stays_single_chunk():
    text = "This is a short document."
    chunks = split_text(text)
    assert len(chunks) == 1
    assert chunks[0].page_content == text


def test_split_chunk_size_respected():
    text = "word " * 500
    chunks = split_text(text, chunk_size=100)
    for chunk in chunks:
        assert len(chunk.page_content) <= 150  # allow overlap headroom
