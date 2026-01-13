"""
authority_bindings.py

Binds explicit authority to an existing Decision.
"""

from datetime import datetime, timedelta, timezone
from typing import Iterable

from core.decision import Authority, Decision


def bind_authority(
    decision: Decision,
    approved_by: str,
    reason: str,
    scope: Iterable[str],
    ttl_seconds: int,
) -> Decision:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    authority = Authority(
        approved_by=approved_by,
        reason=reason,
        scope=list(scope),
        expires_at=expires_at,
    )

    # Return a NEW Decision (immutability preserved)
    return Decision(
        proposal=decision.proposal,
        authority=authority,
        decision_id=decision.decision_id,
        created_at=decision.created_at,
    )
