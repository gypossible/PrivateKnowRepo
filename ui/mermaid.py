import re


def render_mermaid(mermaid_code: str) -> str:
    """Wrap mermaid code in an HTML page that renders it via mermaid.js CDN."""
    # Strip ```mermaid fences if present
    code = mermaid_code.strip()
    code = re.sub(r"^```mermaid\s*", "", code)
    code = re.sub(r"```\s*$", "", code).strip()

    # Escape for HTML embedding
    code_escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    body {{
      margin: 0;
      padding: 16px;
      background: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      display: flex;
      justify-content: center;
    }}
    .mermaid {{
      max-width: 100%;
      overflow-x: auto;
    }}
    .error-box {{
      background: #fff3cd;
      border: 1px solid #ffc107;
      border-radius: 6px;
      padding: 12px;
      font-family: monospace;
      font-size: 13px;
      white-space: pre-wrap;
      display: none;
    }}
  </style>
</head>
<body>
  <div>
    <div class="mermaid" id="diagram">{code_escaped}</div>
    <div class="error-box" id="error-box"></div>
  </div>
  <script>
    mermaid.initialize({{
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
    }});
    mermaid.run({{
      nodes: [document.getElementById('diagram')],
    }}).catch(function(err) {{
      document.getElementById('diagram').style.display = 'none';
      var eb = document.getElementById('error-box');
      eb.style.display = 'block';
      eb.textContent = 'Mermaid render error:\\n' + err.message + '\\n\\nRaw code:\\n{code_escaped}';
    }});
  </script>
</body>
</html>"""
    return html
