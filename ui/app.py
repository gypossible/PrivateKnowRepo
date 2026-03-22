import os
import sys

import gradio as gr

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NotebookConfig
from agent.graph import NotebookAgent
from ui.mermaid import render_mermaid


def create_app():
    config = NotebookConfig()
    agent = NotebookAgent(config)

    # ── Event handlers ──────────────────────────────────────────────

    def on_send(message: str, history: list):
        if not message.strip():
            return history, gr.update(visible=False), ""
        answer, diagram_code = agent.chat(message, history)
        history = history + [[message, answer]]
        if diagram_code:
            html = render_mermaid(diagram_code)
            return history, gr.update(value=html, visible=True), ""
        else:
            return history, gr.update(visible=False), ""

    def on_upload(files):
        if not files:
            return "No files selected.", agent.vector_store.doc_count()
        total = 0
        names = []
        for f in files:
            try:
                count = agent.ingest_file(f.name, os.path.basename(f.name))
                total += count
                names.append(os.path.basename(f.name))
            except Exception as e:
                names.append(f"{os.path.basename(f.name)} (error: {e})")
        status = f"Indexed {total} chunks from: {', '.join(names)}"
        return status, agent.vector_store.doc_count()

    def on_web_search(query: str):
        if not query.strip():
            return "Please enter a search query."
        try:
            count = agent.ingest_web_search(query)
            return f"Added {count} results for: '{query}' — Total chunks: {agent.vector_store.doc_count()}"
        except Exception as e:
            return f"Search failed: {e}"

    def on_clear():
        agent.vector_store.clear()
        return "Knowledge base cleared.", 0

    def on_refresh():
        count = agent.vector_store.doc_count()
        index_exists = os.path.exists(config.faiss_index_dir)
        return f"Total chunks indexed: {count}\nIndex on disk: {'Yes' if index_exists else 'No'}\nEmbedding model: {config.embedding_model}"

    # ── Gradio Layout ────────────────────────────────────────────────

    with gr.Blocks(
        title="Notebook Agent",
        theme=gr.themes.Soft(),
        css=".gradio-container { max-width: 900px !important; }",
    ) as demo:
        gr.Markdown(
            """# 📓 Notebook Research Agent
            > 上传文档或搜索网络资料，然后精准提问 · 支持生成 Mermaid 图表"""
        )

        with gr.Tabs():

            # ── Tab 1: Chat ──────────────────────────────────────────
            with gr.Tab("💬 Chat"):
                chatbot = gr.Chatbot(
                    height=460,
                    label="Conversation",
                    bubble_full_width=False,
                )
                with gr.Row():
                    msg_box = gr.Textbox(
                        placeholder="Ask a question, or say 'draw a flowchart of...'",
                        scale=5,
                        show_label=False,
                        container=False,
                    )
                    send_btn = gr.Button("Send ➤", variant="primary", scale=1, min_width=80)

                diagram_output = gr.HTML(label="Diagram", visible=False)

                send_btn.click(
                    on_send,
                    inputs=[msg_box, chatbot],
                    outputs=[chatbot, diagram_output, msg_box],
                )
                msg_box.submit(
                    on_send,
                    inputs=[msg_box, chatbot],
                    outputs=[chatbot, diagram_output, msg_box],
                )

            # ── Tab 2: Upload Documents ──────────────────────────────
            with gr.Tab("📂 Upload Documents"):
                gr.Markdown("Upload PDF, TXT, DOCX, or MD files to add them to the knowledge base.")
                file_upload = gr.File(
                    file_types=[".pdf", ".txt", ".docx", ".md"],
                    file_count="multiple",
                    label="Select files",
                )
                upload_btn = gr.Button("Index Files", variant="primary")
                upload_status = gr.Textbox(label="Status", interactive=False, lines=2)
                doc_count = gr.Number(label="Total chunks in knowledge base", interactive=False, value=agent.vector_store.doc_count())

                upload_btn.click(
                    on_upload,
                    inputs=[file_upload],
                    outputs=[upload_status, doc_count],
                )

            # ── Tab 3: Web Search ────────────────────────────────────
            with gr.Tab("🌐 Add Web Sources"):
                gr.Markdown("Search the web and add results to your knowledge base.")
                search_query = gr.Textbox(
                    label="Search query",
                    placeholder="e.g. latest AI research 2025",
                )
                search_btn = gr.Button("Search & Index", variant="primary")
                search_status = gr.Textbox(label="Status", interactive=False, lines=2)

                search_btn.click(
                    on_web_search,
                    inputs=[search_query],
                    outputs=[search_status],
                )

            # ── Tab 4: Knowledge Base Info ───────────────────────────
            with gr.Tab("🗄️ Knowledge Base"):
                kb_info = gr.Textbox(label="Index info", interactive=False, lines=4)
                with gr.Row():
                    refresh_btn = gr.Button("Refresh")
                    clear_btn = gr.Button("Clear Knowledge Base", variant="stop")
                clear_status = gr.Textbox(label="Status", interactive=False)

                refresh_btn.click(on_refresh, outputs=[kb_info])
                clear_btn.click(on_clear, outputs=[clear_status, doc_count])

                # Auto-load info on tab focus
                demo.load(on_refresh, outputs=[kb_info])

    return demo
