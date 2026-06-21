"""Validation for uHOME-bundled household networking policy (regular LAN by default)."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

from uhome_server.config import load_uhome_network_policy_contract


class UHomeNetworkPolicyPayload(BaseModel):
    contract_version: Literal["v2.0.4"]
    profile_id: Literal["lan", "beacon", "crypt", "tomb", "home"]
    network_scope: Literal["public", "private", "household"]
    visibility: Literal["visible", "hidden"]
    auth_mode: Literal["open", "password-protected", "discovery-based"]
    vault_access: Literal["local-only"]
    internet_sharing: Literal["disabled"]
    runtime_owner: Literal["uHOME-server"]
    policy_owner: Literal["uHOME-server"]
    consumer_repos: list[Literal["uHOME-server", "sonic-screwdriver"]] = Field(min_length=1)
    secret_refs: list[str] = Field(default_factory=list)
    notes: Optional[str] = None


def _allowed_values(raw_value: Any) -> set[str]:
    if isinstance(raw_value, list):
        return {str(item) for item in raw_value}
    return {str(raw_value)}


def validate_uhome_network_policy_payload(payload: dict[str, Any]) -> dict[str, Any]:
    model = UHomeNetworkPolicyPayload.model_validate(payload)
    contract = load_uhome_network_policy_contract()
    profile_rules = contract["profiles"][model.profile_id]

    issues: list[str] = []

    if model.network_scope != profile_rules["network_scope"]:
        issues.append(
            f"profile {model.profile_id} requires network_scope={profile_rules['network_scope']}"
        )

    allowed_visibility = _allowed_values(profile_rules["visibility"])
    if model.visibility not in allowed_visibility:
        issues.append(
            f"profile {model.profile_id} requires visibility in {sorted(allowed_visibility)}"
        )

    allowed_auth_modes = _allowed_values(profile_rules["auth_mode"])
    if model.auth_mode not in allowed_auth_modes:
        issues.append(
            f"profile {model.profile_id} requires auth_mode in {sorted(allowed_auth_modes)}"
        )

    if model.vault_access != profile_rules["vault_access"]:
        issues.append(
            f"profile {model.profile_id} requires vault_access={profile_rules['vault_access']}"
        )

    if model.internet_sharing != profile_rules["internet_sharing"]:
        issues.append(
            f"profile {model.profile_id} requires internet_sharing={profile_rules['internet_sharing']}"
        )

    if model.runtime_owner != profile_rules["runtime_owner"]:
        issues.append(
            f"profile {model.profile_id} requires runtime_owner={profile_rules['runtime_owner']}"
        )

    if model.policy_owner != profile_rules["policy_owner"]:
        issues.append(
            f"profile {model.profile_id} requires policy_owner={profile_rules['policy_owner']}"
        )

    allowed_consumers = set(profile_rules["consumer_repos"])
    if "uHOME-server" not in model.consumer_repos:
        issues.append("consumer_repos must include uHOME-server for server-side adoption")
    if not set(model.consumer_repos).issubset(allowed_consumers):
        issues.append(
            f"profile {model.profile_id} allows consumer_repos in {sorted(allowed_consumers)}"
        )

    invalid_secret_refs = [item for item in model.secret_refs if item and not item.startswith("secret://")]
    if invalid_secret_refs:
        issues.append("secret_refs must use symbolic secret:// references only")

    if issues:
        raise ValueError("; ".join(issues))

    return model.model_dump()


def uhome_network_policy_validation_error(exc: ValidationError | ValueError) -> dict[str, Any]:
    if isinstance(exc, ValidationError):
        return {
            "ok": False,
            "error": "uhome-network-policy-validation-failed",
            "issues": exc.errors(),
        }
    return {
        "ok": False,
        "error": "uhome-network-policy-validation-failed",
        "issues": [{"message": str(exc)}],
    }
