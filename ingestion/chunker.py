import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def _tiktoken_len(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def chunk_text(text: str, source: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list[Document]:
    """Split text into overlapping chunks. Returns list of LangChain Documents."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=_tiktoken_len,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )
    chunks = splitter.split_text(text)
    return [
        Document(
            page_content=chunk,
            metadata={"source": source, "chunk_id": i},
        )
        for i, chunk in enumerate(chunks)
    ]
