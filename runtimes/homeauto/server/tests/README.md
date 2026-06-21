# Tests

`tests/` is a canonical root.

This directory holds the runtime safety checks for the standalone server and the
information-architecture transition. The current suite is still organized as a
single flat test root because the active package remains intact under
`src/uhome_server/`.

Current coverage includes:

- config and CLI behavior
- dashboard, runtime, Home Assistant, and presentation routes
- installer bundle, staging, promotion, and live-apply contracts
- network registry and library-runtime behavior
- new tests should target `uhome_server.installer` rather than deprecated
  `uhome_server.sonic` imports
