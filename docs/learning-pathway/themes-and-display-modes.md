# Themes and display modes (family overview)

Cross-repo reference for how uDOS picks **colours**, **skins**, **adapters**, and **guided step flows** across browser, ThinUI, shell TUI, and publish surfaces.

Implementation lives primarily in **`uDOS-themes`**. GUI ownership boundaries are in **`uDOS-dev`** `docs/gui-system-family-contract.md`.

## Start in `uDOS-themes`

| Topic | Document |
| --- | --- |
| Display modes (browser, ThinUI, TUI, workflow, publish, forms) | `uDOS-themes/docs/display-modes.md` |
| Token schema and `theme-tokens.json` | `uDOS-themes/docs/theme-token-standard.md` |
| Step-by-step forms and presentation rules | `uDOS-themes/docs/step-form-presentation-rules.md` |
| Registries (themes / adapters / skins) and rollout | `uDOS-themes/docs/adapter-skin-registry-plan.md` |
| ThinUI, workflow, Prose, GTX integration plan | `uDOS-themes/docs/integration-thinui-workflow-prose-gtx.md` |

## Sibling repos

- **Workspace web shell** loads browser-default tokens: `uDOS-workspace/apps/web/src/lib/theme/` (sync from themes via `uDOS-themes/scripts/sync-theme-tokens-to-workspace.sh`).
- **ThinUI** bridge: `uDOS-thinui/docs/themes-sibling-bridge.md`.
- **Shell TUI parity** with themes adapters: `uDOS-shell/docs/tui-themes-parity.md`.

## Publishing and library hub (same repo)

How the static library site and GitHub-hosted markdown relate to themes work:

| Topic | Document |
| --- | --- |
| Site generation and Pages | `uDOS-docs/docs/publishing-architecture.md` |
| Canonical edit locations | `uDOS-docs/docs/local-vs-github-docs-boundary.md` |
| Onboarding and course hooks | `uDOS-docs/docs/course-hooks-and-onboarding.md` |

## Cursor lane

Workspace **06** (themes and display modes) — `uDOS-dev/docs/cursor-focused-workspaces.md` § Workspace 06; round notes under `uDOS-dev/@dev/notes/rounds/`.

When both `uDOS-docs` and `uDOS-themes` sit in the same family checkout, open the paths above relative to each repo root.
