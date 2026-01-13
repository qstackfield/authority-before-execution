"""
authority_bindings.py

Explicit authority binding helpers.

Authority is attached deliberately at runtime.
Nothing here infers, scores, or automates approval.

If authority is missing, expired, or out of scope,
execution must fail.
"""

from typing import Dict, List
from datetime import datetime, timedelta


def bind_authority(
    decision: Dict,
    *,
    approved_by: str,
    reason: str,
    scope: List[str],
    ttl_seconds: int = 60,
) -> Dict:
    """
    Bind explicit, time-bound, scoped authority to a decision.

    This function does NOT mutate the original decision.
    It returns a new decision with an authority artifact
    that must be validated at execution time.
    """

    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

    enriched = dict(decision)
    enriched["authority"] = {
        "approved_by": approved_by,
        "reason": reason,
        "scope": scope,
        "issued_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    return enriched
