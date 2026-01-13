"""
executor.py

Execution boundary for authority-gated actions.

This is the only location where execution is permitted.
All allow/deny outcomes are traced at this boundary.
"""

from __future__ import annotations

from typing import Dict, Any

from opik import track, configure

from core.decision import Decision
from core.authority_gate import (
    enforce_authority,
    AuthorityMissing,
    AuthorityExpired,
    AuthorityScopeViolation,
    decision_snapshot,
)

# Initialize Opik using environment or ~/.opik.config
configure()


@track(
    name="execution.commit",
    capture_input=True,
    capture_output=True,
)
def execute(decision: Decision) -> Dict[str, Any]:
    """
    Attempt execution of a decision.

    This function never raises.
    It returns a structured result describing allow/deny outcomes.
    """

    decision_id = decision.decision_id
    action = decision.proposal.action

    try:
        enforce_authority(decision)

        authority = decision.authority
        overbroad = False

        if authority and authority.scope is None:
            overbroad = True

        return {
            "status": "executed",
            "execution_allowed": True,
            "deny_reason": None,
            "decision_id": decision_id,
            "action": action,
            "params": decision.proposal.params,
            "authority_overbroad": overbroad,
            "decision_snapshot": decision_snapshot(decision),
        }

    except AuthorityMissing as e:
        return {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "missing_authority",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
            "authority_overbroad": False,
        }

    except AuthorityExpired as e:
        return {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "expired_authority",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
            "authority_overbroad": False,
        }

    except AuthorityScopeViolation as e:
        return {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "scope_violation",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
            "authority_overbroad": False,
        }
