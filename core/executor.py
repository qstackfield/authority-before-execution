"""
executor.py

Execution boundary for authority-gated actions.

This is the only place where state change is allowed.
All allow/deny outcomes are traced via Opik at the execution boundary.
"""

from __future__ import annotations

from opik import track, configure

from core.authority_gate import (
    enforce_authority,
    AuthorityMissing,
    AuthorityExpired,
    AuthorityScopeViolation,
)

# Initialize Opik using existing config/env (OPIK_* vars or ~/.opik.config).
# This must live ONLY at the execution boundary.
configure()


@track(
    name="execution.commit",
    capture_input=True,
    capture_output=True,
)
def execute(decision: dict) -> dict:
    """
    Execute a decision only if authority is valid at runtime.

    This function never throws.
    It returns a structured allow/deny result so callers can reason
    about execution outcomes deterministically.
    """

    decision_id = decision.get("decision_id")
    action = decision.get("action")

    try:
        enforce_authority(decision)

        return {
            "status": "executed",
            "execution_allowed": True,
            "deny_reason": None,
            "decision_id": decision_id,
            "action": action,
            "params": decision.get("params"),
        }

    except AuthorityMissing as e:
        return {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "missing_authority",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
        }

    except AuthorityExpired as e:
        return {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "expired_authority",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
        }

    except AuthorityScopeViolation as e:
        return {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "scope_violation",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
        }
