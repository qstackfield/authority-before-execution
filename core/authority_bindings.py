"""
authority_bindings.py

Explicit authority binding helpers.

Authority is attached deliberately at runtime.
Nothing here infers, scores, or automates approval.
"""

from typing import Dict


def bind_authority(
    decision: Dict,
    *,
    approved_by: str,
    reason: str
) -> Dict:
    """
    Bind explicit authority to a decision.

    This mutates nothing implicitly — it returns
    a new decision with authority attached.
    """
    enriched = dict(decision)

    enriched["authority"] = {
        "approved_by": approved_by,
        "reason": reason
    }

    return enriched
