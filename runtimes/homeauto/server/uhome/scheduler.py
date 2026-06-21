from __future__ import annotations

class Scheduler:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def add(self, name: str, schedule: str) -> dict:
        event = {"name": name, "schedule": schedule, "enabled": True}
        self.events.append(event)
        return event

    def list(self) -> dict:
        return {"count": len(self.events), "events": self.events}
