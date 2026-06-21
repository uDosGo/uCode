from __future__ import annotations

from pydantic import ValidationError

from uhome_server.sync_records import SyncRecordEnvelope, validate_sync_record_envelope


def _valid_envelope() -> dict:
    return {
        "contract_version": "v2.0.4",
        "contacts": [
            {
                "contact_id": "contact:jane-smith",
                "entity_type": "canonical_contact",
                "display_name": "Jane Smith",
                "given_name": "Jane",
                "family_name": "Smith",
                "role_title": "Director",
                "company": "Acme Co",
                "relationship": "client",
                "notes": "Primary contact.",
                "emails": [{"label": "work", "value": "jane@example.com", "primary": True}],
                "phones": [{"label": "mobile", "value": "+61400000000", "primary": True}],
                "addresses": [{"label": "work", "city": "Brisbane", "country": "Australia"}],
                "websites": [{"label": "company", "value": "https://example.com", "primary": True}],
                "social_profiles": [{"platform": "linkedin", "handle": "jane-smith", "url": "https://linkedin.com/in/jane-smith"}],
                "external_refs": [{"system": "vault_contacts_db", "ref": "vault-contact-001", "matched": True, "merge_confidence": 1}],
                "source_provenance": [{"source": "vault", "observed_at": "2026-03-15T00:00:00Z", "note": "Imported from local vault."}],
                "first_seen_at": "2026-03-01T00:00:00Z",
                "last_seen_at": "2026-03-15T00:00:00Z",
            }
        ],
        "activities": [
            {
                "activity_id": "activity:followup-task",
                "entity_type": "activity",
                "activity_kind": "task",
                "title": "Prepare follow-up note",
                "body": "Summarize the meeting and route to CRM.",
                "status": "open",
                "occurred_at": "2026-03-15T00:00:00Z",
                "due_at": "2026-03-16T00:00:00Z",
                "completed_at": None,
                "contact_refs": [{"kind": "contact", "id": "contact:jane-smith"}],
                "company_refs": [{"kind": "company", "id": "company:acme-co"}],
                "binder_refs": [{"kind": "binder", "id": "binder:client-followup"}],
                "source_provenance": [{"source": "vault", "observed_at": "2026-03-15T00:00:00Z"}],
                "sync": {"state": "pending", "last_attempt_at": "2026-03-15T00:00:00Z"},
            }
        ],
        "binders": [
            {
                "object_id": "binder:client-followup",
                "entity_type": "binder_project",
                "object_kind": "binder",
                "canonical_tag": "#binder/client-followup",
                "title": "Client Follow-up",
                "summary": "Binder for ongoing contact follow-up.",
                "status": "active",
                "contact_refs": [{"kind": "contact", "id": "contact:jane-smith"}],
                "company_refs": [{"kind": "company", "id": "company:acme-co"}],
                "routing": {"projection_targets": ["hubspot-activity", "google-doc"], "automation_labels": ["followup"]},
                "source_provenance": [{"source": "vault", "observed_at": "2026-03-15T00:00:00Z"}],
                "sync": {"state": "pending", "last_attempt_at": "2026-03-15T00:00:00Z"},
            }
        ],
        "sync_metadata": [
            {
                "sync_id": "sync:followup-task-hubspot",
                "entity_type": "sync_metadata",
                "subject": {"kind": "activity", "id": "activity:followup-task"},
                "source_system": "vault",
                "target_system": "hubspot",
                "direction": "push",
                "state": "pending",
                "last_attempt_at": "2026-03-15T00:00:00Z",
                "last_success_at": None,
                "next_retry_at": None,
                "error_code": None,
                "error_message": None,
            }
        ],
    }


def test_sync_record_envelope_validates() -> None:
    envelope = validate_sync_record_envelope(_valid_envelope())
    assert isinstance(envelope, SyncRecordEnvelope)
    assert envelope.contract_version == "v2.0.4"
    assert envelope.contacts[0].contact_id == "contact:jane-smith"
    assert envelope.binders[0].routing.projection_targets == ["hubspot-activity", "google-doc"]


def test_sync_record_envelope_rejects_invalid_contract_version() -> None:
    payload = _valid_envelope()
    payload["contract_version"] = "v2.0.3"
    try:
        validate_sync_record_envelope(payload)
    except ValidationError as exc:
        assert "v2.0.4" in str(exc)
    else:
        raise AssertionError("expected ValidationError")
