from tavily import TavilyClient
from langchain_core.documents import Document


class WebSearcher:
    def __init__(self, api_key: str, max_results: int = 4):
        self.client = TavilyClient(api_key=api_key)
        self.max_results = max_results

    def search(self, query: str) -> list[dict]:
        resp = self.client.search(query, max_results=self.max_results)
        return resp.get("results", [])

    def search_and_format(self, query: str) -> str:
        results = self.search(query)
        if not results:
            return ""
        lines = [f"Web search results for: {query}\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r.get('title', '')}\nURL: {r.get('url', '')}\n{r.get('content', '')}\n")
        return "\n".join(lines)

    def search_to_chunks(self, query: str) -> list[Document]:
        results = self.search(query)
        docs = []
        for r in results:
            content = f"{r.get('title', '')}\n{r.get('content', '')}"
            docs.append(Document(
                page_content=content,
                metadata={"source": r.get("url", "web"), "chunk_id": 0},
            ))
        return docs
