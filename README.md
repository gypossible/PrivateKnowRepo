---
title: PrivateKnowRepo
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.40.0
app_file: app.py
pinned: false
---

# PrivateKnowRepo — NotebookLM-Style Research Agent

A NotebookLM-inspired AI agent that lets you upload documents or search the web, then ask precise questions and generate Mermaid diagrams from your knowledge base.

## Features

- 📄 **File Upload** — PDF, TXT, DOCX, MD
- 🌐 **Web Search** — Tavily-powered real-time search, auto-indexed
- �� **RAG Q&A** — Precise answers with source citations
- 🗺️ **Mermaid Diagrams** — Auto-generate flowcharts, mindmaps, sequence diagrams
- 💬 **Gradio Web UI** — Clean browser interface

## Tech Stack

- **LLM**: Google Gemini 1.5 Pro
- **Orchestration**: LangGraph
- **Embeddings**: sentence-transformers (local)
- **Vector Store**: FAISS
- **Web Search**: Tavily
- **UI**: Gradio
