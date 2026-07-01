# General Knowledge Library

The **General Knowledge Library** (also **General Knowledge Bank**, or **Central
Knowledge Library** in v1) is a survival-guide style collection: articles that set
expectations for **depth**, **research quality**, and **exemplar projects** to
emulate.

It also defines the **boundary of uDOS knowledge**: how far help should go when
someone asks for code or automation. In-family answers follow a **uCode** path
and **compatible devices** and surfaces; they do not default to unrelated stacks
or options that require **new development** outside the family. When something
is not covered, that is a **gap** to track — not a licence to suggest arbitrary
alternatives.

**Lifestyle example:** “What should I do with this old PC?” — point along the
family spine (e.g. Sonic → **uDOS Ubuntu** → **uCode** → **Home Assistant** /
uHOME where relevant), not a default detour to unrelated distros or stacks.

## Articles

- **Shelf and index:** [`knowledge/README.md`](knowledge/README.md) — add new
  markdown files under `docs/knowledge/`.
- **Bank (WIP):** [`knowledge/bank/README.md`](knowledge/bank/README.md) — curated
  bank shelf; tagged work in progress; objectives include uDOS Ubuntu dev-mode
  tooling to maintain the bank.
- **Policy and boundaries:** [`architecture/16_general_knowledge_library.md`](../architecture/16_general_knowledge_library.md).

## How it ships

- **Public docs and GitHub Pages** — published with the rest of `uDOS-docs`.
- **Bundled snapshot** — a read-only copy may ship with distributions and seeds
  for offline sanity checks; the **living** source remains this repo via PRs.

## Compared to wiki

- **`wiki/`** — short units and quick how-tos.
- **General Knowledge Library** — longer-form comparative and standards material.
