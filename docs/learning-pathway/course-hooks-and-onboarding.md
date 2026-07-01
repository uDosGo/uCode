# Course hooks, onboarding funnels, and ownership

Where **onboarding**, **wiki units**, and **course-style** material live, and how they connect to the public library.

## Ownership

| Lane | Owner | Location | Notes |
| --- | --- | --- | --- |
| **Onboarding (shortest path in)** | `uDOS-docs` | `docs/onboarding.md` | Linked from Learning Hub in `family-source.json`. |
| **Family learning order** | `uDOS-docs` | `architecture/07_family_learning_path.md` | High-level module sequence. |
| **Wiki units (per module)** | Each product repo | `<repo>/wiki/unit-*.md` | Listed in `library_pages` → learning → Wiki Units cards and `wiki_units` array. Examples: `uDOS-host/wiki/`, `uDOS-workspace/wiki/` when those repos ship units. |
| **Courses and resources** | `uDOS-docs` metadata | `family-source.json` → `courses_and_resources` | External URLs, playlists, or future first-party course stubs. |
| **General Knowledge Library** | `uDOS-docs` | `docs/knowledge/` | Long-form articles; separate from wiki units. |
| **Operator / Cursor handoff** | `uDOS-dev` | `docs/cursor-execution.md`, round notes | Not surfaced on public learning hub by default. |

## Onboarding funnel (recommended)

1. **Library home** (`site/index.html`) → Learning Hub.
2. **Learning Hub** → `onboarding.md` → Family Learning Path.
3. **Learning Path** → pick a **track** (runtime / surface / operations) or a **wiki unit** for hands-on.
4. **Reference Hub** → policies, host docs, **publishing** and **themes** reader pages as they are added to featured references.

## Adding a new wiki unit

1. Add the markdown file under the owning repo’s `wiki/`.
2. Add a card under **library_pages** → learning (Wiki Units section) and an entry in **`wiki_units`** if the manifest should list it.
3. Run **`generate-site-data.mjs`** and verify **Learning** and **manifest** pages.

## Adding a course hook

1. Prefer **`courses_and_resources`** in `family-source.json` for external or bundled links.
2. For a first-party course outline in git, add a doc under `docs/` or `architecture/` and link it from the Learning Hub **Guides** section or `courses_and_resources`.

## Related

- `docs/publishing-architecture.md`
- `docs/knowledge/README.md`
- `site/data/family-source.json`
