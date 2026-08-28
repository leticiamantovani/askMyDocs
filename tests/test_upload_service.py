import io
from uuid import uuid4

import pytest

from app.core.config import settings
from app.core.exceptions import PayloadTooLargeError, ValidationError
from app.services import upload_service
from tests.pdf_fixtures import make_pdf

USER = uuid4()


class FakeUpload:
    """Stands in for UploadFile: the service only touches .file and .filename."""

    def __init__(self, data: bytes, filename: str = "doc.pdf"):
        self.file = io.BytesIO(data)
        self.filename = filename


class FakeDb:
    def __init__(self):
        self.executed = []

    async def execute(self, statement, params=None):
        self.executed.append(params)

    async def commit(self):
        pass


async def upload(data: bytes, db=None):
    return await upload_service.upload_pdf_service(USER, FakeUpload(data), db or FakeDb())


@pytest.mark.asyncio
async def test_oversized_pdf_is_rejected_before_parsing(monkeypatch):
    monkeypatch.setattr(settings, "max_pdf_bytes", 100)
    with pytest.raises(PayloadTooLargeError, match="larger than"):
        await upload(make_pdf(["page one"]))


@pytest.mark.asyncio
async def test_empty_upload_is_rejected():
    with pytest.raises(ValidationError, match="empty"):
        await upload(b"")


@pytest.mark.asyncio
async def test_non_pdf_is_rejected_even_with_a_pdf_filename():
    with pytest.raises(ValidationError, match="not a PDF"):
        await upload(b"GIF89a" + b"\x00" * 500)


@pytest.mark.asyncio
async def test_corrupt_pdf_gives_a_readable_error(monkeypatch):
    monkeypatch.setattr(upload_service, "index_chunks", _boom)
    with pytest.raises(ValidationError, match="Could not read the PDF"):
        await upload(make_pdf(["ok"]))


@pytest.mark.asyncio
async def test_image_only_pdf_is_rejected_instead_of_creating_an_empty_document(monkeypatch):
    """A PDF with no extractable text would index zero chunks and break chat."""
    monkeypatch.setattr(upload_service, "index_chunks", _zero)
    db = FakeDb()
    with pytest.raises(ValidationError, match="No text could be extracted"):
        await upload(make_pdf(["scanned"]), db)
    assert db.executed, "the empty collection should be cleaned up"


@pytest.mark.asyncio
async def test_failed_upload_drops_the_half_written_collection(monkeypatch):
    monkeypatch.setattr(upload_service, "index_chunks", _boom)
    db = FakeDb()
    with pytest.raises(ValidationError):
        await upload(make_pdf(["ok"]), db)
    assert db.executed and db.executed[0]["name"].startswith(f"user_{USER}_")


async def _boom(chunks, collection_name):
    raise RuntimeError("embedding backend exploded")


async def _zero(chunks, collection_name):
    return 0
