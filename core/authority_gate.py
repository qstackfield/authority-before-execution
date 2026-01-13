"""
authority_gate.py

This module enforces a single invariant:

    No action may execute unless explicit authority
    has been bound to the decision at runtime.

This is intentionally minimal. Authority is not inferred,
scored, or guessed. It must be present.
"""


class AuthorityMissing(Exception):
    pass


def enforce_authority(decision: dict) -> None:
    """
    Enforce that a decision carries explicit authority.

    Expected decision shape:
        {
            "action": str,
            "params": dict,
            "authority": {
                "approved_by": str,
                "reason": str
            }
        }
    """
    authority = decision.get("authority", {})

    if authority is None:
        raise AuthorityMissing("Execution blocked: authority not bound")

    if not authority.get("approved_by"):
        raise AuthorityMissing("Execution blocked: authority missing approver")

    if not authority.get("reason"):
        raise AuthorityMissing("Execution blocked: authority missing justification")
