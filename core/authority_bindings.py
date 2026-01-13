"""
authority_bindings.py

Explicit authority binding helpers.

Authority is attached deliberately at runtime.
Nothing here infers, scores, or automates approval.
If authority is missing or expired, execution must fail.
"""

from typing import Dict
from datetime import datetime, timedelta


def bind_authority(
    decision: Dict,
    *,
    approved_by: str,
    reason: str,
    ttl_seconds: int = 60
) -> Dict:
    """
    Bind explicit, time-bound authority to a decision.

    This function does not mutate the original decision.
    It returns a new decision with an authority artifact
    that must be validated at execution time.
    """

    now = datetime.utcnow()

    enriched = dict(decision)

    enriched["authority"] = {
        "approved_by": approved_by,
        "reason": reason,
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=ttl_seconds)).isoformat()
    }

    return enriched
