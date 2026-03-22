import json
import re
from langchain_core.messages import HumanMessage, SystemMessage
from .state import AgentState
from .prompts import ROUTER_PROMPT, RAG_SYSTEM_PROMPT, DIAGRAM_PROMPT


def _format_docs(docs: list) -> str:
    if not docs:
        return "No documents in knowledge base."
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[{i}] Source: {source}\n{doc.page_content}")
    return "\n\n".join(parts)


def router_node(state: AgentState, llm) -> dict:
    prompt = ROUTER_PROMPT.format(query=state["query"])
    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content.strip()
    # Strip markdown fences if present
    text = re.sub(r"```json|```", "", text).strip()
    try:
        data = json.loads(text)
        return {
            "needs_web_search": bool(data.get("needs_web_search", False)),
            "needs_diagram": bool(data.get("needs_diagram", False)),
        }
    except Exception:
        return {"needs_web_search": False, "needs_diagram": False}


def retrieval_node(state: AgentState, vector_store, top_k: int = 6) -> dict:
    docs = vector_store.search(state["query"], k=top_k)
    return {"retrieved_docs": docs}


def web_search_node(state: AgentState, searcher) -> dict:
    if not state.get("needs_web_search"):
        return {"web_results": ""}
    formatted = searcher.search_and_format(state["query"])
    return {"web_results": formatted}


def answer_node(state: AgentState, llm) -> dict:
    docs_text = _format_docs(state.get("retrieved_docs", []))
    web_text = state.get("web_results", "")
    web_context = f"=== Web Search Results ===\n{web_text}" if web_text else ""

    system = RAG_SYSTEM_PROMPT.format(
        retrieved_docs=docs_text,
        web_context=web_context,
    )
    messages = [SystemMessage(content=system)] + list(state.get("messages", [])) + [HumanMessage(content=state["query"])]
    response = llm.invoke(messages)
    return {"answer": response.content, "diagram_code": ""}


def diagram_node(state: AgentState, llm) -> dict:
    docs_text = _format_docs(state.get("retrieved_docs", []))
    prompt = DIAGRAM_PROMPT.format(query=state["query"], retrieved_docs=docs_text)
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()

    # Extract mermaid code block
    match = re.search(r"```mermaid\s*([\s\S]+?)```", raw)
    if match:
        diagram_code = match.group(1).strip()
    else:
        # Fallback: use entire response if it looks like mermaid
        diagram_code = raw

    explanation = f"Here is the diagram based on your knowledge base. (Generated from {len(state.get('retrieved_docs', []))} relevant sections)"
    return {"answer": explanation, "diagram_code": diagram_code}
