import os
import shutil
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


class NotebookVectorStore:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", index_dir: str = "./faiss_index"):
        self.index_dir = index_dir
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.store: FAISS | None = None

    def load_existing(self):
        if os.path.exists(self.index_dir):
            try:
                self.store = FAISS.load_local(
                    self.index_dir,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
            except Exception:
                self.store = None

    def add_documents(self, docs: list[Document]) -> int:
        if not docs:
            return 0
        if self.store is None:
            self.store = FAISS.from_documents(docs, self.embeddings)
        else:
            self.store.add_documents(docs)
        self.store.save_local(self.index_dir)
        return len(docs)

    def search(self, query: str, k: int = 6) -> list[Document]:
        if self.store is None:
            return []
        return self.store.similarity_search(query, k=k)

    def doc_count(self) -> int:
        if self.store is None:
            return 0
        return self.store.index.ntotal

    def clear(self):
        if os.path.exists(self.index_dir):
            shutil.rmtree(self.index_dir)
        self.store = None
