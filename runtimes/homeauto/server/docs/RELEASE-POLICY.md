# uHOME Server Release Policy

**Version**: 1.0  
**Last Updated**: 2026-03-10  
**Status**: Active

## Overview

This document defines the release engineering policies and procedures for uHOME Server. It covers versioning strategy, release workflow, quality gates, and distribution channels.

## Semantic Versioning

uHOME Server follows [Semantic Versioning 2.0.0](https://semver.org/).

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

**Examples**:
- `1.0.0` — Stable release
- `1.1.0-alpha.1` — Pre-release (alpha)
- `1.1.0-beta.2` — Pre-release (beta)
- `1.1.0-rc.1` — Release candidate
- `1.1.0+20260310` — Build metadata (optional)

### Version Increment Rules

**MAJOR version** (X.0.0) — Increment when:
- Breaking changes to REST API contracts
- Removal of deprecated features
- Incompatible changes to storage/registry formats
- Changes requiring operator intervention (migration scripts)

**MINOR version** (0.X.0) — Increment when:
- New features added (backward compatible)
- New API endpoints added
- Deprecations announced (not removed)
- Significant operational improvements

**PATCH version** (0.0.X) — Increment when:
- Bug fixes (backward compatible)
- Security patches
- Documentation updates
- Performance improvements (no API changes)

### Pre-release Versions

**Alpha** (`-alpha.N`):
- Early development, unstable
- API may change without notice
- Not recommended for production

**Beta** (`-beta.N`):
- Feature-complete for the release
- API stabilizing, only critical changes allowed
- Suitable for testing environments

**Release Candidate** (`-rc.N`):
- Final testing before stable release
- No new features, only bug fixes
- Production-ready pending final validation

## Version Storage

### Primary Sources of Truth

1. **`pyproject.toml`** — Canonical source
   ```toml
   [project]
   name = "uhome-server"
   version = "1.0.0"
   ```

2. **`src/uhome_server/__init__.py`** — Python module version
   ```python
   __version__ = "1.0.0"
   ```

3. **Git Tags** — Release markers
   ```
   v1.0.0
   v1.1.0-beta.1
   ```

### Version Synchronization

All three sources must be kept in sync. Use the version bumping workflow (see below) to ensure consistency.

## Release Workflow

### 1. Pre-Release Checklist

- [ ] All tests passing (`pytest tests/`)
- [ ] No known critical bugs
- [ ] Documentation updated (README, API docs, runbooks)
- [ ] CHANGELOG updated with release notes
- [ ] Version number decided (MAJOR/MINOR/PATCH)
- [ ] Migration guide written (if breaking changes)

### 2. Version Bump

**Update version in all locations**:

```bash
# 1. Update pyproject.toml
sed -i '' 's/^version = ".*"/version = "1.1.0"/' pyproject.toml

# 2. Update __init__.py
sed -i '' 's/^__version__ = ".*"/__version__ = "1.1.0"/' src/uhome_server/__init__.py

# 3. Verify consistency
grep -n "version" pyproject.toml
grep -n "__version__" src/uhome_server/__init__.py
```

**OR use automation** (future enhancement):
```bash
# Proposed CLI command
uhome version bump --type minor  # or major, patch
```

### 3. Commit and Tag

```bash
# Stage version changes
git add pyproject.toml src/uhome_server/__init__.py

# Commit with conventional format
git commit -m "chore: bump version to 1.1.0"

# Create annotated tag
git tag -a v1.1.0 -m "Release v1.1.0: [Brief Summary]

- Feature: Added backup/restore utilities
- Feature: Health and readiness endpoints
- Enhancement: Observability documentation
- Bug fix: Fixed registry sync timing issue

See CHANGELOG.md for full details."

# Push commit and tag
git push origin main
git push origin v1.1.0
```

### 4. Create GitHub Release

**Via GitHub Web Interface**:
1. Navigate to: `https://github.com/fredporter/uHomeNest/releases/new`
2. Select tag: `v1.1.0`
3. Release title: `uHOME Server v1.1.0`
4. Description: Copy from CHANGELOG.md + git tag message
5. Attach artifacts (optional): tarball, wheel
6. Mark as pre-release if applicable
7. Publish release

**Via GitHub CLI** (future automation):
```bash
gh release create v1.1.0 \
  --title "uHOME Server v1.1.0" \
  --notes-file CHANGELOG_v1.1.0.md \
  --latest
```

### 5. Distribution

**PyPI** (future):
```bash
# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

**Docker Hub** (future):
```bash
docker build -t uhome/uhome-server:1.1.0 .
docker push uhome/uhome-server:1.1.0
docker tag uhome/uhome-server:1.1.0 uhome/uhome-server:latest
docker push uhome/uhome-server:latest
```

### 6. Post-Release

- [ ] Update documentation sites (if applicable)
- [ ] Announce release (GitHub Discussions, Slack, etc.)
- [ ] Monitor for critical issues (first 24-48 hours)
- [ ] Prepare hotfix release if needed

## CHANGELOG Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

### Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Feature XYZ

### Changed
- Modified behavior of ABC

### Deprecated
- Feature DEF will be removed in v2.0.0

### Removed
- N/A

### Fixed
- Bug in GHI

### Security
- Patched vulnerability in JKL

## [1.1.0] - 2026-03-15

### Added
- Health and readiness endpoints for monitoring
- Backup/restore CLI commands
- Observability documentation

### Changed
- Improved error messages in cluster registry

### Fixed
- Registry sync timing issue in multi-node scenarios

## [1.0.0] - 2026-03-01

Initial stable release.
```

### Category Guidelines

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be-removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

## Hotfix Process

For critical bugs in production releases:

**1. Branch from release tag**:
```bash
git checkout -b hotfix/v1.0.1 v1.0.0
```

**2. Fix the bug**:
```bash
# Make fix
git add .
git commit -m "fix: critical bug in X"
```

**3. Bump PATCH version**:
Follow version bump workflow for PATCH increment.

**4. Merge to main and tag**:
```bash
git checkout main
git merge hotfix/v1.0.1
git tag -a v1.0.1 -m "Hotfix release v1.0.1"
git push origin main v1.0.1
```

**5. Create GitHub release** (as above).

## Release Cadence

**Planned Schedule**:
- **Major releases**: Annual or as-needed for breaking changes
- **Minor releases**: Monthly or bi-monthly
- **Patch releases**: As-needed for critical bugs
- **Pre-releases**: Ad-hoc during development cycles

**Exceptions**:
- Security vulnerabilities: Immediate patch release
- Critical production bugs: Emergency hotfix within 24-48 hours

## Quality Gates

### Automated Checks (CI)

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code coverage ≥ 80%
- [ ] Linting passes (flake8, black, mypy)
- [ ] No high-severity security vulnerabilities (Dependabot, Snyk)

### Manual Checks

- [ ] Smoke test on clean Ubuntu 20.04 LTS
- [ ] Deployment guide walkthrough
- [ ] Backup/restore round-trip validation
- [ ] Multi-node cluster test (if applicable)
- [ ] Runbook procedures validated

### Release Approval

**Minor/Major Releases**:
- Requires: Lead maintainer approval
- Review by: At least one other contributor

**Patch/Hotfix Releases**:
- Requires: Any maintainer approval (expedited for emergencies)

## Deprecation Policy

**Notice Period**: Minimum 1 MINOR release cycle before removal.

**Example Timeline**:
- v1.5.0: Feature X deprecated, warning on console
- v1.6.0: Feature X still present, deprecation warning persists
- v2.0.0: Feature X removed (MAJOR version bump)

**Deprecation Announcement**:
- Update CHANGELOG with `### Deprecated` section
- Add runtime warning (if applicable)
- Update documentation with migration path
- Mention in release notes

## Rollback Strategy

If a release introduces critical issues:

**1. Immediate response**:
- Document issue in GitHub Issues
- Pin users to previous stable version in README

**2. Prepare hotfix**:
- Follow hotfix process above
- Test thoroughly in staging environment

**3. Communicate**:
- Post rollback guidance in GitHub Discussions
- Update documentation with known issues

**4. Learn and improve**:
- Conduct post-mortem
- Add automated tests to prevent recurrence
- Update quality gates if needed

## Tooling and Automation

### Current (Manual)

- Version bumping: Manual `sed` commands
- Tagging: Manual `git tag`
- Release notes: Manual CHANGELOG editing
- GitHub Releases: Manual via web interface

### Future (Automated)

**Proposed**:
- `uhome version bump` CLI command
- GitHub Actions for automated releases
- Automated CHANGELOG generation from conventional commits
- PyPI publishing via CI/CD
- Docker Hub publishing via CI/CD

**Example GitHub Action** (future):
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build distribution
        run: python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
      - name: Create GitHub Release
        uses: actions/create-release@v1
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: CHANGELOG.md
```

## Distribution Channels

### Current

- **GitHub Releases**: Primary distribution (source tarball)
- **Git Repository**: Direct clone for developers

### Future

- **PyPI**: Python package distribution
- **Docker Hub**: Container images
- **Homebrew**: macOS package manager
- **APT Repository**: Debian/Ubuntu packages

## Version Support Policy

**Active Support**:
- Current MAJOR version: Full support (features, bug fixes, security)
- Previous MAJOR version: Security fixes only (6-12 months)

**End-of-Life (EOL)**:
- MAJOR versions older than previous: No support (encourage upgrade)

**Example**:
- v2.x.x: Active (full support)
- v1.x.x: Security fixes only (until v2 + 12 months)
- v0.x.x: EOL (no support)

## Security Releases

For security vulnerabilities:

**1. Private disclosure**:
- Report via GitHub Security Advisories
- Coordinate fix with maintainers

**2. Patch development**:
- Develop fix in private branch
- Backport to supported versions

**3. Coordinated disclosure**:
- Publish security advisory
- Release patch versions simultaneously
- Announce via all channels (GitHub, mailing list, etc.)

**4. Post-release**:
- Update security documentation
- Credit reporter (if desired)

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)

## Document History

- **v1.0 (2026-03-10)**: Initial release policy for Phase 6
