"""
authority_gate.py

Execution enforcement for authority-bound decisions.

No action may execute unless explicit authority
is present, valid, unexpired, and scoped for
the action being performed.
"""

from datetime import datetime
from typing import Dict, List


class AuthorityMissing(Exception):
    pass


class AuthorityExpired(Exception):
    pass


class AuthorityScopeViolation(Exception):
    pass


def enforce_authority(decision: Dict) -> Dict:
    """
    Enforce authority-before-execution.

    Authority must:
    - exist
    - include an expiry
    - be unexpired at execution time
    - explicitly authorize the requested action
    """

    authority = decision.get("authority")

    if not authority:
        raise AuthorityMissing("Execution blocked: authority not bound")

    expires_at = authority.get("expires_at")
    scope: List[str] = authority.get("scope", [])

    if not expires_at:
        raise AuthorityMissing("Execution blocked: authority missing expiry")

    now = datetime.utcnow()
    expiry = datetime.fromisoformat(expires_at)

    if now > expiry:
        raise AuthorityExpired("Execution blocked: authority expired")

    action = decision.get("action")

    if action not in scope:
        raise AuthorityScopeViolation(
            f"Execution blocked: authority does not permit action '{action}'"
        )

    # Execution permitted
    return {
        "status": "executed",
        "action": action,
        "params": decision.get("params"),
    }
