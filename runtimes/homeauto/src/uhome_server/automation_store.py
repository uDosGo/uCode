"""Minimal file-backed automation job and result store for uHOME-server."""

from __future__ import annotations

from typing import Any

from uhome_server.config import get_runtime_settings, read_json_file, utc_now_iso_z, write_json_file


def _job_store_paths() -> tuple:
    settings = get_runtime_settings()
    base_dir = settings.uhome_bank_dir / "automation"
    return base_dir / "jobs.json", base_dir / "results.json"


def _default_jobs() -> dict[str, Any]:
    return {"contract_version": "v2.0.4", "updated_at": None, "items": []}


class AutomationStore:
    def __init__(self, jobs_path=None, results_path=None) -> None:
        default_jobs_path, default_results_path = _job_store_paths()
        self.jobs_path = jobs_path or default_jobs_path
        self.results_path = results_path or default_results_path

    def _load_jobs(self) -> dict[str, Any]:
        return read_json_file(self.jobs_path, default=_default_jobs())

    def _load_results(self) -> dict[str, Any]:
        return read_json_file(self.results_path, default=_default_jobs())

    def _save_jobs(self, payload: dict[str, Any]) -> None:
        write_json_file(self.jobs_path, payload, indent=2)

    def _save_results(self, payload: dict[str, Any]) -> None:
        write_json_file(self.results_path, payload, indent=2)

    def status(self) -> dict[str, Any]:
        jobs = self._load_jobs()
        results = self._load_results()
        return {
            "contract_version": "v2.0.4",
            "owner": "uHOME-server",
            "jobs_path": str(self.jobs_path),
            "results_path": str(self.results_path),
            "queued_jobs": len(jobs.get("items", [])),
            "recorded_results": len(results.get("items", [])),
        }

    def queue_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        jobs = self._load_jobs()
        item = {
            "contract_version": "v2.0.4",
            "job_id": payload.get("job_id") or f"job:{utc_now_iso_z()}",
            "requested_capability": payload.get("requested_capability") or "local-task",
            "payload_ref": payload.get("payload_ref") or "memory://pending",
            "origin_surface": payload.get("origin_surface") or "uHOME-kiosk",
            "policy_flags": payload.get("policy_flags") or {},
            "queued_at": payload.get("queued_at") or utc_now_iso_z(),
        }
        workflow_id = item["policy_flags"].get("workflow_id") if isinstance(item["policy_flags"], dict) else None
        step_id = item["policy_flags"].get("step_id") if isinstance(item["policy_flags"], dict) else None
        if workflow_id:
            item["workflow_id"] = workflow_id
        if step_id:
            item["step_id"] = step_id
        jobs["items"] = [*jobs.get("items", []), item]
        jobs["updated_at"] = utc_now_iso_z()
        self._save_jobs(jobs)
        return item

    def _find_job(self, job_id: str) -> dict[str, Any] | None:
        jobs = self._load_jobs()
        for item in jobs.get("items", []):
            if item.get("job_id") == job_id:
                return item
        return None

    def record_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        results = self._load_results()
        item = {
            "contract_version": "v2.0.4",
            "job_id": payload.get("job_id") or "job:unknown",
            "status": payload.get("status") or "completed",
            "output_refs": payload.get("output_refs") or [],
            "event_refs": payload.get("event_refs") or [],
            "completed_at": payload.get("completed_at") or utc_now_iso_z(),
            "suggested_workflow_action": payload.get("suggested_workflow_action") or "advance",
        }
        if payload.get("workflow_id"):
            item["workflow_id"] = payload["workflow_id"]
        results["items"] = [*results.get("items", []), item]
        results["updated_at"] = utc_now_iso_z()
        self._save_results(results)
        return item

    def list_jobs(self) -> dict[str, Any]:
        return self._load_jobs()

    def list_results(self) -> dict[str, Any]:
        return self._load_results()

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        jobs = self._load_jobs()
        items = list(jobs.get("items", []))
        remaining = [item for item in items if item.get("job_id") != job_id]
        if len(remaining) == len(items):
            return {"contract_version": "v2.0.4", "status": "missing", "job_id": job_id}
        jobs["items"] = remaining
        jobs["updated_at"] = utc_now_iso_z()
        self._save_jobs(jobs)
        result = self.record_result(
            {
                "job_id": job_id,
                "workflow_id": next((item.get("workflow_id") for item in items if item.get("job_id") == job_id), None),
                "status": "cancelled",
                "output_refs": [],
                "event_refs": [f"event://automation/{job_id}/cancelled"],
                "suggested_workflow_action": "pause",
            }
        )
        return {"contract_version": "v2.0.4", "status": "cancelled", "job_id": job_id, "result": result}

    def retry_job(self, job_id: str) -> dict[str, Any]:
        results = self._load_results()
        prior = None
        for item in reversed(results.get("items", [])):
            if item.get("job_id") == job_id:
                prior = item
                break
        if prior is None:
            return {"contract_version": "v2.0.4", "status": "missing", "job_id": job_id}

        retry_payload = {
            "job_id": f"{job_id}:retry",
            "requested_capability": "retry-task",
            "payload_ref": prior.get("output_refs", ["memory://retry"])[0] if prior.get("output_refs") else "memory://retry",
            "origin_surface": "uHOME-server",
            "policy_flags": {
                "workflow_id": prior.get("workflow_id"),
                "retried_from": job_id,
            },
        }
        queued = self.queue_job(retry_payload)
        return {"contract_version": "v2.0.4", "status": "queued", "job": queued, "retried_from": job_id}

    def process_next_job(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        jobs = self._load_jobs()
        items = list(jobs.get("items", []))
        if not items:
            return {"contract_version": "v2.0.4", "status": "noop", "reason": "no-queued-jobs"}

        job = items.pop(0)
        jobs["items"] = items
        jobs["updated_at"] = utc_now_iso_z()
        self._save_jobs(jobs)

        result_payload = {
            "job_id": job["job_id"],
            "workflow_id": job.get("workflow_id"),
            "status": (payload or {}).get("status") or "completed",
            "output_refs": (payload or {}).get("output_refs")
            or [f"memory://automation/results/{job['job_id']}"],
            "event_refs": (payload or {}).get("event_refs") or [f"event://automation/{job['job_id']}"],
            "completed_at": (payload or {}).get("completed_at") or utc_now_iso_z(),
            "suggested_workflow_action": (payload or {}).get("suggested_workflow_action") or "advance",
        }
        result = self.record_result(result_payload)
        return {"contract_version": "v2.0.4", "status": "processed", "job": job, "result": result}


def get_automation_store() -> AutomationStore:
    return AutomationStore()
