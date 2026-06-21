"""Rules engine service for DVR scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class RuleType(Enum):
    TIME_BASED = "time-based"
    SERIES = "series"
    MOVIE = "movie"
    KEYWORD = "keyword"
    CHANNEL = "channel"


class QualityProfile(Enum):
    SD = "sd"
    HD = "hd"
    UHD = "uhd"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class BaseRule:
    rule_id: str
    rule_name: str
    rule_type: RuleType
    enabled: bool = True
    priority: Priority = Priority.MEDIUM
    quality_profile: QualityProfile = QualityProfile.HD
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TimeBasedRule(BaseRule):
    channel_id: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class SeriesRule(BaseRule):
    series_id: str = ""
    series_title: str = ""


@dataclass
class MovieRule(BaseRule):
    movie_id: str = ""
    movie_title: str = ""


@dataclass
class KeywordRule(BaseRule):
    keywords: list[str] = field(default_factory=list)


@dataclass
class ChannelRule(BaseRule):
    channel_id: str = ""
    channel_name: str = ""


class RulesEngine:
    def __init__(self, persistence_path: Path | None = None):
        self.rules: dict[str, BaseRule] = {}
        self.persistence_path = persistence_path

    def create_rule(self, rule_data: dict) -> BaseRule:
        import uuid
        rule_id = rule_data.get("rule_id", str(uuid.uuid4()))
        rule_type_str = rule_data.get("rule_type", "time-based")
        rule_type = RuleType(rule_type_str)

        rule = BaseRule(
            rule_id=rule_id,
            rule_name=rule_data.get("rule_name", "Unnamed Rule"),
            rule_type=rule_type,
            enabled=rule_data.get("enabled", True),
            priority=Priority(rule_data.get("priority", 2)),
            quality_profile=QualityProfile(rule_data.get("quality_profile", "hd")),
        )
        self.rules[rule_id] = rule
        return rule

    def get_rule(self, rule_id: str) -> Optional[BaseRule]:
        return self.rules.get(rule_id)

    def list_rules(self) -> list[BaseRule]:
        return list(self.rules.values())

    def update_rule(self, rule_id: str, updates: dict) -> Optional[BaseRule]:
        rule = self.rules.get(rule_id)
        if not rule:
            return None
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        rule.updated_at = datetime.now()
        return rule

    def delete_rule(self, rule_id: str) -> bool:
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        rule = self.rules.get(rule_id)
        if not rule:
            return False
        rule.enabled = True
        return True

    def disable_rule(self, rule_id: str) -> bool:
        rule = self.rules.get(rule_id)
        if not rule:
            return False
        rule.enabled = False
        return True


_engine: RulesEngine | None = None


def get_rules_engine(persistence_path: Path | None = None) -> RulesEngine:
    global _engine
    if _engine is None:
        _engine = RulesEngine(persistence_path=persistence_path)
    return _engine
