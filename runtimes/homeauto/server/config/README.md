# Config

The `config/` root is the stable checked-in configuration lane for the pathway
refactor.

Current config surfaces still live elsewhere:

- `defaults/workspace/` for shared workspace defaults
- `memory/config/uhome.json` for runtime-local server config
- environment variables for optional runtime overrides

Checked-in operator examples:

- `environment.example.env` for service environment variables
- `base-runtime-profile.example.json` for runtime profile examples

Operator guide:

- `../docs/ENVIRONMENT-CONFIGURATION.md`

Planned use of this root:

- checked-in schemas and examples
- role and host-profile templates
- pathway-readable configuration docs that are not mixed into runtime state
- base runtime profile examples that stay separate from Matter extension
  definitions
