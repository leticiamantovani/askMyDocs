from collections.abc import Iterable, Iterator

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return [Document(page_content=t) for t in splitter.split_text(text)]


def iter_chunks(
    pages: Iterable[str],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    buffer_chars: int | None = None,
) -> Iterator[Document]:
    """Split a stream of pages into chunks without materialising the document.

    Pages are accumulated into a small buffer before splitting so a chunk is
    never cut short at a page boundary: the trailing piece is carried over into
    the next buffer instead of being emitted. Peak memory is buffer_chars,
    independent of how many pages arrive.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    limit = buffer_chars if buffer_chars is not None else chunk_size * 20
    buffer = ""

    for page in pages:
        buffer += page + "\n"
        if len(buffer) < limit:
            continue
        pieces = splitter.split_text(buffer)
        for piece in pieces[:-1]:
            yield Document(page_content=piece)
        buffer = pieces[-1] if pieces else ""

    for piece in splitter.split_text(buffer):
        yield Document(page_content=piece)
