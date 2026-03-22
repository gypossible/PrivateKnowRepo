from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    query: str
    retrieved_docs: list[dict]
    web_results: str
    needs_web_search: bool
    needs_diagram: bool
    answer: str
    diagram_code: str
    sources: list[str]
