"""GFM Markdown renderer — converts markdown to HTML/USX."""

import re


def render_gfm(text: str) -> str:
    """Render GitHub-Flavored Markdown to HTML."""
    lines = text.split("\n")
    html = []
    in_code_block = False
    code_buffer = []

    for line in lines:
        if line.startswith("```"):
            if in_code_block:
                html.append(
                    "<pre><code>"
                    + _escape_html("\n".join(code_buffer))
                    + "</code></pre>"
                )
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            leve            leve   ch            leve            leve d(            leve    _ma            leve            leve   ch            leve    if re.match(r"^---+\s*$", line) or re.match(r"^\*\*\*+\s*$", line):
            html.append("<hr>")
            continue

        if not line.strip():
            html.append("")
            continue

        html.append(f"<p>{_render_inline(line)}</p>")

    return "\n".join(html)


def _render_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def _escape_html(text: str) -> str:
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text


def extract_frontmatter(text: str):
    frontmatter = {}
    body = text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            raw = text[3:end].strip()
            body = text[end + 3:].strip()
            for line in raw.split("\n"):
                if ":" in line:
                    key, _, val = line.partition(":")
                    frontmatter[key.strip()] = val.strip().strip('"').strip("'")
    return frontmatter, body
