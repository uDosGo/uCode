# Defaults

`defaults/` is a transitional compatibility root.

This directory remains active because `uHOME-server` still participates in
shared workspace and component-default flows with `uDOS`. During Phase 1, it is
not replaced or renamed.

Current role:

- checked-in workspace defaults for the `uhome` component
- compatibility surface for shared template workspace behavior

Longer-term direction:

- keep shared defaults here while stable tracked configuration grows under
  `config/`
- avoid mixing machine-local runtime state into this root
