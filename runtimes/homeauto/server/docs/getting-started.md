# Getting started (uHomeNest v3.9)

1. Review `docs/boundary.md` and `docs/base-runtime-boundary.md` so local runtime ownership stays inside **uHomeNest**.
2. Run `QUICKSTART.md` for the first runnable API and route checks (regular LAN baseline).
3. Review `examples/basic-uhome-server-session.md` for the smallest standalone operator smoke.
4. Run the repo validation entrypoint before and after runtime changes:

```bash
bash scripts/run-uhome-server-checks.sh
```

5. For direct local use, launch the console/kiosk surface with:

```bash
bash scripts/first-run-launch.sh
```

6. For Ubuntu-class host readiness, run:

```bash
bash scripts/check-prereqs.sh --storage-path /media/library --workspace-path ~/.workspace
```

1. Keep service code under `services/` and `modules/`.
1. Route scheduling behavior through `scheduling/`.
1. Put new Matter or Home Assistant extension contracts in `uHOME-matter`.
1. Add tests before extending persistent behavior.
