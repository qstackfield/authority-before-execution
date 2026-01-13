"""
authority_bindings.py

Responsible for binding explicit authority to a Decision.

This module does not validate authority.
It constructs authority artifacts that are later enforced
at the execution boundary.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Iterable

from core.decision import Decision, Authority


def bind_authority(
    decision: Decision,
    *,
    approved_by: str,
    reason: str,
    scope: Optional[Iterable[str]],
    ttl_seconds: int,
) -> Decision:
    """
    Bind an authority artifact to a decision.

    - scope=None represents intentionally unscoped authority
    - ttl_seconds defines time-bounded validity
    """

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=ttl_seconds)

    authority = Authority(
        approved_by=approved_by,
        reason=reason,
        scope=list(scope) if scope is not None else None,
        expires_at=expires_at,
    )

    return Decision(
        decision_id=decision.decision_id,
        proposal=decision.proposal,
        authority=authority,
        created_at=decision.created_at,
    )
