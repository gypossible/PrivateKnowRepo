from dataclasses import dataclass, field
import os


@dataclass
class NotebookConfig:
    # LLM
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    llm_model: str = "gemini-1.5-pro"
    temperature: float = 0.3

    # Embeddings (local, no API key needed)
    embedding_model: str = "all-MiniLM-L6-v2"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 150

    # Retrieval
    top_k_docs: int = 6

    # Web search
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    tavily_max_results: int = 4

    # Persistence
    faiss_index_dir: str = "./faiss_index"
