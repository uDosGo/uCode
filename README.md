# uCode - uDosGo Runtimes

## Structure
```
uCode/
├── runtimes/
│   ├── basic/       - BASIC runtime (from uCode1)
│   ├── amos/        - AMOS runtime (from uCode2)
│   ├── homeauto/    - Home automation runtime (from uCode3)
│   └── multimedia/  - Multimedia runtime (from uCode4)
├── shared/          - Shared code across runtimes
├── tests/           - Integration tests
└── README.md        - This file
```

## Quick Start
```bash
# Run a specific runtime
python -m runtimes.basic
python -m runtimes.amos
```

## Development
Each runtime is independent with its own pyproject.toml and tests.
