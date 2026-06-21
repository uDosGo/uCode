"""Server-rendered thin HTML surfaces (Tailwind Typography / prose build scans this file)."""

from __future__ import annotations

import html
from pathlib import Path

import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension

from uhome_server.config import get_repo_root

# Classes referenced for tailwind / @tailwindcss/typography (thin-prose-build)
_PROSE_PAGE_CLASSES = (
    "min-h-screen bg-stone-950 text-stone-100 antialiased "
    "prose prose-invert prose-stone max-w-prose mx-auto px-6 py-10 "
    "prose-headings:font-semibold prose-a:text-amber-400 prose-a:no-underline "
    "hover:prose-a:underline prose-code:text-amber-200"
)
_THIN_SHELL_MAIN = "mx-auto flex min-h-screen max-w-5xl flex-col gap-6 px-4 py-8 text-stone-100"


def thin_reading_page_html(title: str, inner_html: str, *, static_prefix: str = "/static/thin") -> str:
    """Wrap document HTML in a prose column; loads compiled Tailwind+typography CSS."""
    safe_title = html.escape(title, quote=True)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{safe_title}</title>
    <link rel="stylesheet" href="{html.escape(static_prefix, quote=True)}/prose.css">
  </head>
  <body class="bg-stone-950">
    <main class="{_THIN_SHELL_MAIN}">
      <nav class="text-sm text-stone-500">
        <a class="text-amber-400 hover:underline" href="/api/runtime/thin/automation">Thin automation</a>
        <span aria-hidden="true"> · </span>
        <a class="text-amber-400 hover:underline" href="/api/runtime/thin/read">Prose read</a>
      </nav>
      <article class="{_PROSE_PAGE_CLASSES}">
        {inner_html}
      </article>
    </main>
  </body>
</html>"""


def markdown_to_html_fragment(md: str) -> str:
    """Render markdown to an HTML fragment for Tailwind Typography (`prose`)."""
    return markdown.markdown(
        md,
        extensions=[
            "nl2br",
            TableExtension(),
            FencedCodeExtension(),
        ],
        output_format="html5",
    )


def default_read_mode_markdown() -> str:
    return """# uHOME thin read mode

Tailwind **Typography** (`prose`) is enabled for long-form reading and light browsing inside the uHOME server thin surface.

## What this is

- Server-rendered HTML with a compiled `@tailwindcss/typography` stylesheet.
- **Plain markdown** reading only — not a uDOS Workspace or **#binder** document shell.
- Optional future: family **logs / feeds / spool** (see uDOS-dev candidate note); not committed in stable `docs/` yet.

## Links

- [Automation status (thin GUI)](/api/runtime/thin/automation)
- [Runtime readiness JSON](/api/runtime/ready)
- [Browse `docs/pathway/README.md`](/api/runtime/thin/browse?rel=pathway/README.md) (repo checkout only)

## Note

For Cursor workspace **03** closure, open this page in a real browser to confirm the prose layout and navigation.
"""


def thin_read_mode_html() -> str:
    body = markdown_to_html_fragment(default_read_mode_markdown())
    return thin_reading_page_html("uHOME thin read", body)


def thin_read_mode_from_path(path: Path) -> tuple[str, int]:
    """Load markdown from path under repo root; 404 if outside or missing."""
    root = get_repo_root().resolve()
    try:
        target = path.resolve()
    except OSError:
        return "Invalid path", 404
    if root not in target.parents and target != root:
        return "Path outside repository", 404
    if not target.is_file():
        return "Not found", 404
    try:
        md = target.read_text(encoding="utf-8")
    except OSError:
        return "Unreadable", 404
    body = markdown_to_html_fragment(md)
    title = target.name
    return thin_reading_page_html(title, body), 200


def thin_automation_status_html() -> str:
    """Thin automation dashboard; links to prose read mode for browsing."""
    from uhome_server.automation_store import get_automation_store

    store = get_automation_store()
    status = store.status()
    jobs = store.list_jobs().get("items", [])
    results = store.list_results().get("items", [])
    latest_result = results[-1] if results else None
    latest_job = jobs[-1] if jobs else None
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>uHOME Thin Automation</title>
    <link rel="stylesheet" href="/static/thin/prose.css">
  </head>
  <body class="bg-stone-950 text-stone-100 antialiased">
    <main class="{_THIN_SHELL_MAIN}">
      <nav class="text-sm text-stone-500">
        <a class="text-amber-400 hover:underline" href="/api/runtime/thin/read">Prose read / browse</a>
      </nav>
      <div class="grid gap-4 md:grid-cols-3">
        <section class="rounded-2xl border border-amber-900/40 bg-stone-900/80 p-5 shadow-lg">
          <p class="text-xs uppercase tracking-widest text-amber-500/90">uHOME Thin</p>
          <h1 class="mt-2 text-2xl font-semibold text-stone-50">Automation Status</h1>
          <p class="mt-2 text-sm text-stone-400">Runtime view for queued work and latest completion state.</p>
        </section>
        <section class="rounded-2xl border border-stone-700 bg-stone-900/60 p-5">
          <p class="text-xs uppercase tracking-widest text-stone-500">Queued Jobs</p>
          <p class="mt-2 text-3xl font-semibold text-amber-400">{status.get("queued_jobs", 0)}</p>
        </section>
        <section class="rounded-2xl border border-stone-700 bg-stone-900/60 p-5">
          <p class="text-xs uppercase tracking-widest text-stone-500">Recorded Results</p>
          <p class="mt-2 text-3xl font-semibold text-amber-400">{status.get("recorded_results", 0)}</p>
        </section>
      </div>
      <section class="prose prose-invert prose-stone mt-4 max-w-none rounded-2xl border border-stone-700 bg-stone-900/40 px-6 py-5">
        <h2 class="text-stone-100">Latest activity</h2>
        <ul>
          <li><strong>Latest queued job:</strong> {html.escape(str(latest_job.get("job_id", "none") if latest_job else "No queued jobs yet."))}</li>
          <li><strong>Latest result:</strong> {html.escape(str(latest_result.get("job_id", "none") if latest_result else "No recorded results yet."))}
            {html.escape(" — " + str(latest_result.get("status", "")) if latest_result else "")}</li>
        </ul>
      </section>
    </main>
  </body>
</html>"""
