# PrivateKnowRepo — NotebookLM-Style Research Agent

A NotebookLM-inspired AI agent that lets you upload documents or search the web, then ask precise questions and generate Mermaid diagrams from your knowledge base.

## Features

- 📄 **File Upload** — PDF, TXT, DOCX, MD
- 🌐 **Web Search** — Tavily-powered real-time search, auto-indexed
- 🤖 **RAG Q&A** — Precise answers with source citations
- 🗺️ **Mermaid Diagrams** — Auto-generate flowcharts, mindmaps, sequence diagrams
- 💬 **Gradio Web UI** — Clean browser interface

## Setup

### 1. Clone & install
```bash
git clone https://github.com/gypossible/PrivateKnowRepo.git
cd PrivateKnowRepo
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file:
```
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 3. Run
```bash
python main.py
```
Open http://localhost:7860

## Usage

1. **Upload Documents** tab → upload PDF/TXT/DOCX/MD files
2. **Add Web Sources** tab → enter a topic to search and index
3. **Chat** tab → ask questions or say "画一个流程图" to get a Mermaid diagram

## Tech Stack

- **LLM**: Google Gemini 1.5 Pro
- **Orchestration**: LangGraph
- **Embeddings**: sentence-transformers (local)
- **Vector Store**: FAISS
- **Web Search**: Tavily
- **UI**: Gradio
