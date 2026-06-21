# Package compat provides uDOS-core contract compatibility
import json
from typing import Dict, Any


class AutomationJob:
    def __init__(self, job_id: str, job_type: str, payload: Dict[str, Any], created_at: str):
        self.id = job_id
        self.type = job_type
        self.payload = payload
        self.created_at = created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "created_at": self.created_at
        }


def load_contract(path: str) -> AutomationJob:
    """Load from uDOS-core contract path"""
    with open(path, 'r') as f:
        data = json.load(f)
    return AutomationJob(
        job_id=data["id"],
        job_type=data["type"],
        payload=data["payload"],
        created_at=data["created_at"]
    )
