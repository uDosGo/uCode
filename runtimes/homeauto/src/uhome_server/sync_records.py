"""Typed sync-record models aligned to the uHOME-bundled sync-record contract.

`binder` / `binder_project` / `binders` mirror optional family JSON shapes for
`integrated-udos` clients. uHOME does not expose binder workflows in product UI;
see `docs/contributor-dev-brief.md` and `docs/ROADMAP-V4.md`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError


ContactRefId = str
ActivityRefId = str
BinderRefId = str
SyncRefId = str


class SyncRecordModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EntityRef(SyncRecordModel):
    kind: Literal["contact", "company", "binder", "project", "activity"]
    id: str = Field(min_length=1)


class LabeledValue(SyncRecordModel):
    label: str = Field(min_length=1)
    value: str = Field(min_length=1)
    primary: bool = False


class Address(SyncRecordModel):
    label: str = Field(min_length=1)
    street: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    state_region: Optional[str] = None
    country: Optional[str] = None


class ExternalRef(SyncRecordModel):
    system: Literal[
        "apple_contacts",
        "vault_contacts_db",
        "hubspot",
        "google",
        "manual",
        "local_network",
    ]
    ref: str = Field(min_length=1)
    matched: bool = False
    merge_confidence: Optional[float] = Field(default=None, ge=0, le=1)


class SourceProvenance(SyncRecordModel):
    source: str = Field(min_length=1)
    observed_at: str = Field(min_length=1)
    note: Optional[str] = None


class SyncFingerprint(SyncRecordModel):
    content_hash: Optional[str] = None
    source_etag: Optional[str] = None
    target_etag: Optional[str] = None


class SyncState(SyncRecordModel):
    state: Literal["pending", "running", "synced", "conflict", "error", "skipped"]
    fingerprint: Optional[SyncFingerprint] = None
    last_attempt_at: Optional[str] = None
    last_success_at: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class SocialProfile(SyncRecordModel):
    platform: Literal["facebook", "instagram", "linkedin", "other"]
    handle: str = Field(min_length=1)
    url: Optional[str] = None


class CanonicalContact(SyncRecordModel):
    contact_id: str = Field(pattern=r"^contact:[a-z0-9][a-z0-9._-]*$")
    entity_type: Literal["canonical_contact"]
    display_name: str = Field(min_length=1)
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    role_title: Optional[str] = None
    company: Optional[str] = None
    relationship: Optional[str] = None
    notes: Optional[str] = None
    emails: List[LabeledValue]
    phones: List[LabeledValue]
    addresses: List[Address]
    websites: List[LabeledValue] = Field(default_factory=list)
    social_profiles: List[SocialProfile] = Field(default_factory=list)
    external_refs: List[ExternalRef]
    source_provenance: List[SourceProvenance]
    first_seen_at: str = Field(min_length=1)
    last_seen_at: str = Field(min_length=1)


class Activity(SyncRecordModel):
    activity_id: str = Field(pattern=r"^activity:[a-z0-9][a-z0-9._-]*$")
    entity_type: Literal["activity"]
    activity_kind: Literal["task", "note", "email", "meeting", "reminder", "issue", "event", "webhook"]
    title: str = Field(min_length=1)
    body: Optional[str] = None
    status: Literal["open", "queued", "in_progress", "done", "cancelled", "failed"]
    occurred_at: Optional[str] = None
    due_at: Optional[str] = None
    completed_at: Optional[str] = None
    contact_refs: List[EntityRef]
    company_refs: List[EntityRef] = Field(default_factory=list)
    binder_refs: List[EntityRef]
    source_provenance: List[SourceProvenance]
    sync: SyncState


class Routing(SyncRecordModel):
    projection_targets: List[str]
    automation_labels: List[str] = Field(default_factory=list)


class BinderProject(SyncRecordModel):
    object_id: str = Field(pattern=r"^(binder|project):[a-z0-9][a-z0-9._-]*$")
    entity_type: Literal["binder_project"]
    object_kind: Literal["binder", "project"]
    canonical_tag: str = Field(pattern=r"^#(binder|project)/[a-z0-9][a-z0-9._-]*$")
    title: str = Field(min_length=1)
    summary: Optional[str] = None
    status: Literal["draft", "active", "paused", "blocked", "archived", "completed"]
    contact_refs: List[EntityRef] = Field(default_factory=list)
    company_refs: List[EntityRef] = Field(default_factory=list)
    routing: Routing
    source_provenance: List[SourceProvenance]
    sync: SyncState


class SyncMetadata(SyncRecordModel):
    sync_id: str = Field(pattern=r"^sync:[a-z0-9][a-z0-9._-]*$")
    entity_type: Literal["sync_metadata"]
    subject: EntityRef
    source_system: str = Field(min_length=1)
    target_system: str = Field(min_length=1)
    direction: Literal["push", "pull", "bidirectional"]
    state: Literal["pending", "running", "synced", "conflict", "error", "skipped"]
    last_attempt_at: str = Field(min_length=1)
    last_success_at: Optional[str] = None
    next_retry_at: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class SyncRecordEnvelope(SyncRecordModel):
    contract_version: Literal["v2.0.4"]
    contacts: List[CanonicalContact]
    activities: List[Activity]
    binders: List[BinderProject]
    sync_metadata: List[SyncMetadata]


def load_sync_record_envelope(path: str) -> SyncRecordEnvelope:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return SyncRecordEnvelope.model_validate(payload)


def validate_sync_record_envelope(payload: Dict[str, Any]) -> SyncRecordEnvelope:
    return SyncRecordEnvelope.model_validate(payload)


def validation_error_payload(exc: ValidationError) -> Dict[str, object]:
    return {
        "ok": False,
        "error": "sync-record-validation-failed",
        "issues": exc.errors(),
    }
