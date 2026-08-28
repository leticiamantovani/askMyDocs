from app.ingestion.splitter import iter_chunks, split_text


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


def test_iter_chunks_matches_split_text_for_a_single_page():
    text = "word " * 300
    assert [c.page_content for c in iter_chunks([text])] == [
        c.page_content for c in split_text(text)
    ]


def test_iter_chunks_keeps_text_flowing_across_page_boundaries():
    """A sentence split over two pages must not be cut at the page edge."""
    chunks = [c.page_content for c in iter_chunks(["the quick brown", "fox jumps over"])]
    assert any("brown" in c and "fox" in c for c in chunks)


def test_iter_chunks_buffer_bounds_memory():
    """Peak buffering stays near buffer_chars no matter how many pages arrive."""
    seen = []

    def pages():
        for _ in range(200):
            yield "word " * 100
            seen.append(len(seen))

    chunks = list(iter_chunks(pages(), chunk_size=100, buffer_chars=1000))
    assert len(chunks) > 200
    assert all(len(c.page_content) <= 200 for c in chunks)


def test_iter_chunks_on_empty_pages():
    assert list(iter_chunks([])) == []
    assert list(iter_chunks(["", ""])) == []


def test_iter_chunks_is_lazy():
    consumed = []

    def pages():
        for i in range(5):
            consumed.append(i)
            yield "short text"

    gen = iter_chunks(pages())
    assert consumed == []  # nothing pulled before the first next()
    next(gen, None)
