from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return [Document(page_content=t) for t in splitter.split_text(text)]
