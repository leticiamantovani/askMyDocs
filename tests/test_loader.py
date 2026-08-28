import io

import pytest

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.ingestion.loader import iter_pdf_pages, stream_size, validate_pdf_header
from tests.pdf_fixtures import make_pdf


def test_stream_size_rewinds_for_the_next_reader():
    stream = io.BytesIO(b"abcdef")
    assert stream_size(stream) == 6
    assert stream.tell() == 0


def test_validate_pdf_header_accepts_a_pdf():
    validate_pdf_header(io.BytesIO(make_pdf(["hi"])))


def test_validate_pdf_header_rejects_a_disguised_file():
    with pytest.raises(ValidationError):
        validate_pdf_header(io.BytesIO(b"MZ\x90\x00 not a pdf"))


def test_iter_pdf_pages_yields_one_page_at_a_time():
    stream = io.BytesIO(make_pdf(["first page", "second page"]))
    assert list(iter_pdf_pages(stream)) == ["first page", "second page"]


def test_page_limit_is_enforced(monkeypatch):
    monkeypatch.setattr(settings, "max_pdf_pages", 2)
    stream = io.BytesIO(make_pdf(["a", "b", "c"]))
    with pytest.raises(ValidationError, match="3 pages"):
        list(iter_pdf_pages(stream))


def test_char_limit_stops_a_pdf_bomb_mid_document(monkeypatch):
    """A small file whose text expands past the cap must abort while streaming."""
    monkeypatch.setattr(settings, "max_pdf_chars", 25)
    stream = io.BytesIO(make_pdf(["x" * 20] * 10))

    pages = iter_pdf_pages(stream)
    assert next(pages)  # first page fits
    with pytest.raises(ValidationError, match="maximum supported size"):
        list(pages)


def test_iter_pdf_pages_is_lazy(monkeypatch):
    """Nothing is parsed until the caller iterates, so limits apply per page."""
    monkeypatch.setattr(settings, "max_pdf_pages", 1)
    stream = io.BytesIO(make_pdf(["a", "b"]))
    pages = iter_pdf_pages(stream)  # no exception yet
    with pytest.raises(ValidationError):
        next(pages)
