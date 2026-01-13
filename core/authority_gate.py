"""
authority_gate.py

Execution enforcement for authority-bound decisions.

No action may execute unless explicit authority
is present, time-valid, and scoped to the action
at runtime.
"""

from datetime import datetime
from typing import Dict, List


class AuthorityMissing(Exception):
    """Raised when required authority is absent or malformed."""
    pass


class AuthorityExpired(Exception):
    """Raised when authority exists but is no longer valid."""
    pass


class AuthorityScopeViolation(Exception):
    """Raised when authority does not permit the requested action."""
    pass


def enforce_authority(decision: Dict) -> Dict:
    """
    Enforce authority-before-execution.

    Execution is permitted IFF:
    - authority is present
    - authority has not expired
    - authority scope explicitly allows the action

    All failures fail closed.
    """

    # --- Authority must exist ---
    authority = decision.get("authority")
    if not authority:
        raise AuthorityMissing("Execution blocked: authority not bound")

    # --- Expiry must exist ---
    expires_at = authority.get("expires_at")
    if not expires_at:
        raise AuthorityMissing("Execution blocked: authority missing expiry")

    # --- Authority must be time-valid ---
    now = datetime.utcnow()
    expiry = datetime.fromisoformat(expires_at)

    if now > expiry:
        raise AuthorityExpired("Execution blocked: authority expired")

    # --- Scope must exist ---
    scope: List[str] = authority.get("scope")
    if not scope:
        raise AuthorityMissing("Execution blocked: authority missing scope")

    # --- Action must be in scope ---
    action = decision.get("action")
    if action not in scope:
        raise AuthorityScopeViolation(
            f"Execution blocked: action '{action}' not authorized"
        )

    # --- Execution permitted ---
    return {
        "status": "executed",
        "action": action,
        "params": decision.get("params"),
    }
