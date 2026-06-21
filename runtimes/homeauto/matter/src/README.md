# Source

`src/` is the integration contract lane for `uHOME-matter`.

Current source surfaces include:

- `matter-bridge-contract.json` as the baseline Matter integration contract
- `matter-clone-catalog.json` as the starter clone-definition catalog
- `home-assistant-bridge-definition.json` as the shared Home Assistant bridge
  definition consumed by `uHOME-server`

Boundary rule:

- keep extension contracts here
- keep base runtime behavior in `uHOME-server`
