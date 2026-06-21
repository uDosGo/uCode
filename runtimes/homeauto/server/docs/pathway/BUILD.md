# Build on uHOME (v4)

Use this path to extend the **uHomeNest** runtime. Historical phase milestones and **`@dev/`** binder trees were retired from the repo in **2026-04** (local archive: monorepo **`.compost/cleanup-2026-04-10/`**).

## Start with

1. [`../../../docs/ROADMAP-V4.md`](../../../docs/ROADMAP-V4.md) — product **v4** line
2. [`../architecture/UHOME-SERVER-DEV-PLAN.md`](../architecture/UHOME-SERVER-DEV-PLAN.md) — dev entry and links
3. [`../contributor-dev-brief.md`](../contributor-dev-brief.md)
4. [`../education-dev-brief.md`](../education-dev-brief.md)
5. [`../pathway/REPO-FAMILY.md`](../pathway/REPO-FAMILY.md)
6. [`../howto/UHOME-INSTALL-LANES.md`](../howto/UHOME-INSTALL-LANES.md)
7. [`../../../src/uhome_server/`](../../../src/uhome_server/) — Python package

## Rules

- Treat the two local briefs as governing inputs alongside [`../../../docs/ROADMAP-V4.md`](../../../docs/ROADMAP-V4.md).
- Keep runtime ownership in **`src/uhome_server/`** unless a subtree policy says otherwise.
- Prefer **Markdown + Tailwind Prose** for operator reading; USXD for interchange handoff ([`../../../dev/UNIVERSAL-DEV.md`](../../../dev/UNIVERSAL-DEV.md)).

## Good next targets

- Remove remaining references to the deprecated `uhome_server.sonic` namespace where safe.
- Grow vault-backed examples under [`../../../vault/`](../../../vault/).
- Harden file-backed registries per [`../../../docs/ROADMAP-V4.md`](../../../docs/ROADMAP-V4.md).
