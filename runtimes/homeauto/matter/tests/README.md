# Tests

`tests/` is the extension contract validation lane for `uHOME-matter`.

Current validation contract:

- `scripts/run-uhome-matter-checks.sh` verifies required repo surfaces
- checked-in Matter integration contracts must stay structurally valid
- checked-in clone catalogs and target registries must stay structurally valid
- private local-root references must not leak into tracked repo docs

Phase 1 rule:

- keep tests lightweight and contract-focused
- use `uHOME-server` for base runtime behavior validation
