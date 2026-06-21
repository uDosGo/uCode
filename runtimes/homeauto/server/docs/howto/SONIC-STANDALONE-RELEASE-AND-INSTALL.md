# Sonic Standalone Release and Install Guide

This guide is the canonical v1.5 release/install path for Sonic as a standalone utility.

For v1.5, this standalone lane may be used to ship:

- Sonic by itself
- `uHOME` by itself through Sonic-provisioned bundles or images
- a combined Sonic + `uHOME` deployment image

## v1.5 Runtime Contract

Sonic now ships with an open-box split:

- seeded global catalog: `memory/sonic/seed/sonic-devices.seed.db`
- local user overlay: `memory/sonic/user/sonic-devices.user.db`
- compatibility mirror: `memory/sonic/sonic-devices.db`

## Release Artifacts

Each release build should publish:

- `sonic-stick-<version>-<build-id>.img`
- `sonic-stick-<version>-<build-id>.iso`
- `build-manifest.json`
- `checksums.txt`
- `build-manifest.json.sig`
- `checksums.txt.sig`

## Public Distribution Notes

- Publish release checksums and detached signatures alongside artifacts.
- Include minimum hardware and OS support notes in release notes.
- Keep release notes aligned with `docs/STATUS.md`.
- When targeting `uHOME`, document whether the image exposes thin GUI,
  Steam-console UX, or both.

## Repo-Local Staging Examples

This repo now includes example staged-installer inputs under:

- `examples/installer/probes/standalone-linux.json`
- `examples/installer/probes/dual-boot-steam-node.json`
- `examples/installer/bundles/standalone/`
- `examples/installer/bundles/dual-boot/`

To materialize a staged install directory from the standalone example:

```bash
uhome-installer stage \
  --bundle-dir ./examples/installer/bundles/standalone \
  --probe ./examples/installer/probes/standalone-linux.json \
  --stage-dir ./tmp/uhome-stage-standalone
```

The staged output includes:

- copied component payloads
- `install-plan.json`
- `install-receipt.json`
- `install-state.json`
- generated config payloads
- rollback metadata when a rollback record or token is present
