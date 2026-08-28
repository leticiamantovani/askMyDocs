import pytest

from langchain_core.documents import Document

from app.core.config import settings
from app.ingestion import indexer


class FakeVectorStore:
    def __init__(self):
        self.created = False
        self.batches: list[int] = []

    def create_collection(self):
        self.created = True

    def add_documents(self, docs):
        self.batches.append(len(docs))


@pytest.fixture
def store(monkeypatch):
    fake = FakeVectorStore()
    monkeypatch.setattr(indexer, "get_vector_store", lambda name: fake)
    return fake


@pytest.mark.asyncio
async def test_chunks_are_embedded_in_fixed_size_batches(store, monkeypatch):
    monkeypatch.setattr(settings, "index_batch_size", 10)
    chunks = (Document(page_content=f"chunk {i}") for i in range(25))

    indexed = await indexer.index_chunks(chunks, "col")

    assert indexed == 25
    assert store.batches == [10, 10, 5]  # never the whole document at once
    assert store.created


@pytest.mark.asyncio
async def test_exact_multiple_does_not_emit_an_empty_batch(store, monkeypatch):
    monkeypatch.setattr(settings, "index_batch_size", 5)
    chunks = [Document(page_content="c") for _ in range(10)]

    assert await indexer.index_chunks(chunks, "col") == 10
    assert store.batches == [5, 5]


@pytest.mark.asyncio
async def test_no_chunks_reports_zero(store):
    assert await indexer.index_chunks(iter([]), "col") == 0
    assert store.batches == []


@pytest.mark.asyncio
async def test_source_is_consumed_lazily(store, monkeypatch):
    """The generator must not be drained before batching starts."""
    monkeypatch.setattr(settings, "index_batch_size", 2)
    peak = {"live": 0}

    def source():
        for i in range(6):
            peak["live"] += 1
            yield Document(page_content=f"c{i}")

    await indexer.index_chunks(source(), "col")
    assert store.batches == [2, 2, 2]
