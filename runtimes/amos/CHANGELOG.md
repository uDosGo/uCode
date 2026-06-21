# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-06-16

### Changed
- AMOS shim (`shim/amos_shim.bbc`) moved to uCode1 (`core_py/bbc/amos_shim.bbc`)
  - Sprite/BOB commands belong with the BBC BASIC runtime in uCode1
  - uCode2 remains a thin ProseUI shim only

## [1.0.0] - 2026-06-13

### Added
- Initial release — thin shim wrapping uConnect's ProseUI surface
- `ucode2` CLI entry point that launches ProseUI
- `bin/ucode2-binder` — CLI entry point for ProseUI launch
- MIT License

### Notes
- uCode2 is intentionally thin — it delegates to uConnect's ProseUI surface
- Canonical source: https://github.com/uDosGo/uConnect
- All uCode1 + uCode2 remain open source forever — no cloud, no payment, no tracking

[1.0.1]: https://github.com/uDosGo/uCode2/releases/tag/v1.0.1
[1.0.0]: https://github.com/uDosGo/uCode2/releases/tag/v1.0.0
