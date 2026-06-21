# Docs (`server/docs`)

Monorepo-wide **v4** plan: [`../../docs/ROADMAP-V4.md`](../../docs/ROADMAP-V4.md). Full doc index: [`../../docs/README.md`](../../docs/README.md) ([`MONOREPO.md`](../../docs/MONOREPO.md)).

`docs/` is the **stable reference** lane for the **uHomeNest** monorepo (**v3.9.x**) and **uHOME** product docs, aligned with the
uDOS family split:

| Lane | Location | Role |
| --- | --- | --- |
| Reference | [`docs/`](README.md) (here) | Architecture, clients, ops, specs |
| Wiki | [`../wiki/`](../wiki/README.md) | Short units and quick orientation |
| Learning | [`../learning/`](../learning/README.md) | Study order, courses pointers, uDOS Library links |

Tutorial and student-facing step-through material also lives under
[`courses/`](../courses/README.md) (repo root) with maintainer notes in
`docs/courses/`. This tree is for architecture, pathway, client, operational,
and implementation documentation tied to the real repo.

## Entry Points

### Use

- [../QUICKSTART.md](../QUICKSTART.md) for the fastest local run path
- [../FIRST-TIME-INSTALL.md](../FIRST-TIME-INSTALL.md) for clean-machine setup
- [USE.md](pathway/USE.md) for the current operator path
- [UHOME-DASHBOARD.md](ui/UHOME-DASHBOARD.md) for the dashboard surface
- [BEACON-ACTIVATE.md](clients/BEACON-ACTIVATE.md)
  for local portal and vault-reader positioning
- [SONIC-STANDALONE-RELEASE-AND-INSTALL.md](howto/SONIC-STANDALONE-RELEASE-AND-INSTALL.md)
  for release and install guidance

### Learn

- [README.md](pathway/README.md) in `docs/pathway/` for repo positioning
- [education-dev-brief.md](education-dev-brief.md)
  for the local pathway brief
- [UHOME-v1.5.md](specs/UHOME-v1.5.md) for the current canonical spec

### Build (v4)

- [UHOME-SERVER-DEV-PLAN.md](architecture/UHOME-SERVER-DEV-PLAN.md) — **v4** dev entry (links to monorepo `docs/`)
- [contributor-dev-brief.md](contributor-dev-brief.md) — contributor workflow
- [thin-ui-feature-completion.md](thin-ui-feature-completion.md) — thin UI checklists
- [education-dev-brief.md](education-dev-brief.md) — education-structure brief
- [pathway/BUILD.md](pathway/BUILD.md) — extend the runtime
- [REPO-FAMILY.md](pathway/REPO-FAMILY.md) — family-boundary rules
- The deprecated `uhome_server.sonic` namespace is compatibility-only; new work should use `uhome_server.installer`

## Family library (GitHub Pages)

The **uDOS Library** indexes uHOME repos (Docs / Wiki / Learning links) from
[`uDOS-docs` `site/data/family-source.json`](https://github.com/fredporter/uDOS-docs/blob/main/site/data/family-source.json).
The public **Learning hub** is `https://fredporter.github.io/uDOS-docs/learning.html`
when Pages is deployed.

## Sections

- `architecture/` for repo-shape and migration policy
- `clients/` for downstream client-contract positioning
- `courses/` for maintainer notes about the learning path
- `decisions/` for architectural and product decisions
- `howto/` for operational runbooks
- `pathway/` for cross-repo positioning and entrypoint docs
- `services/` for service-level operational docs
- `specs/` for implementation-facing specifications
- `ui/` for dashboard and client-surface contracts
- `workspace/` for workspace templates and instructions
