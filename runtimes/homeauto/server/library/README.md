# Library

`library/` is a transitional runtime support root.

It currently holds checked-in manifests and support metadata used by the server
for library and container flows. It is not yet fully remapped into the new
module language, so it remains explicit rather than hidden.

Current role:

- git-backed library manifests
- Home Assistant and container metadata
- runtime support for clone and launch flows

Phase 1 rule:

- keep this root active while the capability map lives under `modules/`
- do not treat `library/` as the public architecture language for new docs
