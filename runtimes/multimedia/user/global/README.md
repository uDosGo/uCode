# @transport

Central exchange point for systems to leave/receive documents for continuation.

## Purpose

- **Inbound**: Other systems drop docs here for Vault processing
- **Outbound**: Vault stages docs here for other systems to pick up
- **Continuation**: Cross-system handoff without inbox/outbox noise

## Usage

- Files placed here are synced to remote (unlike @inbox/@outbox)
- Process and move to appropriate vault location when done
- Clean up processed files regularly
