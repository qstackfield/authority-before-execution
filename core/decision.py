"""
decision.py

Defines the canonical decision contract for authority-gated execution.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Iterable
from datetime import datetime, timezone


def _as_utc(dt: datetime) -> datetime:
    """
    Normalize a datetime to timezone-aware UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class Authority:
    approved_by: str
    reason: str
    scope: Optional[Iterable[str]]
    expires_at: Optional[datetime]

    def is_expired(self, now: datetime) -> bool:
        if self.expires_at is None:
            return False

        now_utc = _as_utc(now)
        expires_utc = _as_utc(self.expires_at)

        return now_utc >= expires_utc


@dataclass(frozen=True)
class Proposal:
    action: str
    params: Dict[str, Any]
    rationale: str


@dataclass(frozen=True)
class Decision:
    proposal: Proposal
    authority: Optional[Authority]
    decision_id: str
    created_at: datetime
