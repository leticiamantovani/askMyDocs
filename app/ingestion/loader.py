import os
from collections.abc import Iterator
from typing import BinaryIO

from pypdf import PdfReader

from app.core.config import settings
from app.core.exceptions import ValidationError

PDF_MAGIC = b"%PDF-"


def stream_size(stream: BinaryIO) -> int:
    """Size of an already-buffered upload, without reading it into memory."""
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    return size


def validate_pdf_header(stream: BinaryIO) -> None:
    """Reject non-PDF payloads before handing the stream to pypdf.

    The dropzone's accept filter is UX only - anything can POST to /upload.
    """
    stream.seek(0)
    header = stream.read(len(PDF_MAGIC))
    stream.seek(0)
    if header != PDF_MAGIC:
        raise ValidationError("File is not a PDF.")


def iter_pdf_pages(stream: BinaryIO) -> Iterator[str]:
    """Yield one page of text at a time, never holding the whole document.

    Starlette has already spooled the upload to a temp file on disk, so pypdf
    reads from there and peak memory tracks a single page, not the file size.
    """
    reader = PdfReader(stream)

    page_count = len(reader.pages)
    if page_count > settings.max_pdf_pages:
        raise ValidationError(
            f"PDF has {page_count} pages; the limit is {settings.max_pdf_pages}."
        )

    extracted = 0
    for page in reader.pages:
        text = page.extract_text() or ""
        extracted += len(text)
        # A few MB of compressed PDF can expand into hundreds of MB of text,
        # so the byte limit alone does not bound what we hold here.
        if extracted > settings.max_pdf_chars:
            raise ValidationError(
                "PDF text content exceeds the maximum supported size."
            )
        yield text
