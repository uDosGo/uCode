# Binders And Publishing

## Purpose

Explain the active family model for binders and publishing in v2.

## Binder Rule

A binder is the durable identity that groups related work.

Think of it like this:

- workspace tells you where something lives
- binder tells you what project, topic, or outcome it belongs to
- workflow advances it in bounded steps
- compile packages it into canonical release artifacts

## Publishing Rule

The core rule remains:

- compile creates the canonical artifact
- publish, submit, persist, and execute are downstream outcomes

That distinction matters across the whole family.

## Why It Matters In v2

The family now has multiple delivery surfaces:

- Wizard-facing web publishing
- Beacon Activate local library presentation
- macOS web and email publishing
- future sync or CRM side-effects triggered by `uDOS-empire`

Those surfaces may share modules, but they should all respect the same
compile-first rule.

## Ownership Guidance

- canonical binder and workflow semantics belong with `uDOS-core`
- family explanation belongs in `uDOS-docs`
- runtime-specific publishing behavior belongs with the repo that owns that surface

## User-Owned Publishing

The family should still assume user-owned publishing by default:

- the user owns the source material
- the user owns the release decision
- public publishing is not the same thing as submission or approval

## Practical Distinctions

- web output is not the only valid compile outcome
- local library presentation is not the same thing as public publication
- submission is not the same thing as approval
- persistence is not the same thing as reader-facing presentation

## Next Docs

- `architecture/07_family_learning_path.md`
- `wizard/05_wizard_and_beacon.md`
- `uhome/08_beacon_activate.md`
