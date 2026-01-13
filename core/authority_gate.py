"""
authority_gate.py

Execution enforcement for authority-bound decisions.

No action may execute unless explicit authority
is present and valid at runtime.
"""

from datetime import datetime
from typing import Dict


class AuthorityMissing(Exception):
    pass


class AuthorityExpired(Exception):
    pass


def enforce_authority(decision: Dict) -> Dict:
    """
    Enforce authority-before-execution.

    If authority is missing or expired at execution time,
    execution must fail closed.
    """

    authority = decision.get("authority")

    if not authority:
        raise AuthorityMissing("BLOCKED: Execution blocked: authority not bound")

    expires_at = authority.get("expires_at")

    if not expires_at:
        raise AuthorityMissing("BLOCKED: Execution blocked: authority missing expiry")

    now = datetime.utcnow()
    expiry = datetime.fromisoformat(expires_at)

    if now > expiry:
        raise AuthorityExpired("BLOCKED: Execution blocked: authority expired")

    # Execution permitted
    return {
        "status": "executed",
        "action": decision.get("action"),
        "params": decision.get("params"),
    }
