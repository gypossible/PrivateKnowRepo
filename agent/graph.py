import os
from functools import partial

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from config import NotebookConfig
from vectorstore.faiss_store import NotebookVectorStore
from search.tavily_search import WebSearcher
from ingestion.file_parser import parse_file
from ingestion.chunker import chunk_text
from .state import AgentState
from .nodes import router_node, retrieval_node, web_search_node, answer_node, diagram_node


class NotebookAgent:
    def __init__(self, config: NotebookConfig):
        self.config = config
        self.llm = ChatGoogleGenerativeAI(
            model=config.llm_model,
            temperature=config.temperature,
            google_api_key=config.google_api_key,
        )
        self.vector_store = NotebookVectorStore(
            embedding_model=config.embedding_model,
            index_dir=config.faiss_index_dir,
        )
        self.searcher = WebSearcher(
            api_key=config.tavily_api_key,
            max_results=config.tavily_max_results,
        )
        self.vector_store.load_existing()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("router", partial(router_node, llm=self.llm))
        workflow.add_node("retrieve", partial(retrieval_node, vector_store=self.vector_store, top_k=self.config.top_k_docs))
        workflow.add_node("web_search", partial(web_search_node, searcher=self.searcher))
        workflow.add_node("answer", partial(answer_node, llm=self.llm))
        workflow.add_node("diagram", partial(diagram_node, llm=self.llm))

        workflow.set_entry_point("router")
        workflow.add_edge("router", "retrieve")

        def after_retrieve(state: AgentState) -> str:
            if state.get("needs_web_search"):
                return "web_search"
            if state.get("needs_diagram"):
                return "diagram"
            return "answer"

        def after_web_search(state: AgentState) -> str:
            if state.get("needs_diagram"):
                return "diagram"
            return "answer"

        workflow.add_conditional_edges("retrieve", after_retrieve, {
            "web_search": "web_search",
            "diagram": "diagram",
            "answer": "answer",
        })
        workflow.add_conditional_edges("web_search", after_web_search, {
            "diagram": "diagram",
            "answer": "answer",
        })
        workflow.add_edge("answer", END)
        workflow.add_edge("diagram", END)

        return workflow.compile()

    def ingest_file(self, file_path: str, filename: str) -> int:
        text = parse_file(file_path)
        chunks = chunk_text(text, source=filename, chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap)
        return self.vector_store.add_documents(chunks)

    def ingest_web_search(self, query: str) -> int:
        chunks = self.searcher.search_to_chunks(query)
        return self.vector_store.add_documents(chunks)

    def chat(self, query: str, history: list) -> tuple[str, str]:
        messages = []
        for human, ai in history:
            if human:
                messages.append(HumanMessage(content=human))
            if ai:
                messages.append(AIMessage(content=ai))

        initial_state: AgentState = {
            "messages": messages,
            "query": query,
            "retrieved_docs": [],
            "web_results": "",
            "needs_web_search": False,
            "needs_diagram": False,
            "answer": "",
            "diagram_code": "",
            "sources": [],
        }

        result = self.graph.invoke(initial_state)
        return result.get("answer", ""), result.get("diagram_code", "")
