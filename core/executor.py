"""
executor.py

Execution boundary for authority-gated actions.

This is the ONLY location where state-changing execution is permitted.

Invariant enforced here:
ABE-EXEC-001
"If explicit authority is not present, valid, and in scope at execution time,
the state transition must not occur."

All allow / deny outcomes are enforced, traced, and exported at this boundary.
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
from core.artifact_exporter import export_execution_artifacts


# ──────────────────────────────────────────────────────────────────────────────
# Execution boundary configuration
# ──────────────────────────────────────────────────────────────────────────────

INVARIANT_ID = "ABE-EXEC-001"
ENFORCEMENT_POINT = "execution.commit"

# Initialize Opik using environment variables or ~/.opik.config.
# This MUST live only at the execution boundary.
configure()


@track(
    name=ENFORCEMENT_POINT,
    capture_input=True,
    capture_output=True,
)
def execute(decision: Decision) -> Dict[str, Any]:
    """
    Attempt execution of a decision.

    This function never raises.

    All outcomes are returned as structured results so that:
    - governance is deterministic
    - evaluation is reproducible
    - demos are provable, not narrated
    """

    decision_id = decision.decision_id
    action = decision.proposal.action

    try:
        # ── Authority enforcement (hard gate) ──
        enforce_authority(decision)

        authority = decision.authority
        authority_overbroad = False

        # Overbroad authority = approval with no explicit scope
        if authority and authority.scope is None:
            authority_overbroad = True

        result: Dict[str, Any] = {
            "status": "executed",
            "execution_allowed": True,
            "deny_reason": None,
            "decision_id": decision_id,
            "action": action,
            "params": decision.proposal.params,
            "authority_overbroad": authority_overbroad,
            "invariant_id": INVARIANT_ID,
            "enforcement_point": ENFORCEMENT_POINT,
            "decision_snapshot": decision_snapshot(decision),
        }

        # ── Persist immutable execution proof ──
        export_execution_artifacts(decision, result)

        return result

    except AuthorityMissing as e:
        result = {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "missing_authority",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
            "authority_overbroad": False,
            "invariant_id": INVARIANT_ID,
            "enforcement_point": ENFORCEMENT_POINT,
        }

        export_execution_artifacts(decision, result)
        return result

    except AuthorityExpired as e:
        result = {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "expired_authority",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
            "authority_overbroad": False,
            "invariant_id": INVARIANT_ID,
            "enforcement_point": ENFORCEMENT_POINT,
        }

        export_execution_artifacts(decision, result)
        return result

    except AuthorityScopeViolation as e:
        result = {
            "status": "blocked",
            "execution_allowed": False,
            "deny_reason": "scope_violation",
            "message": str(e),
            "decision_id": decision_id,
            "action": action,
            "authority_overbroad": False,
            "invariant_id": INVARIANT_ID,
            "enforcement_point": ENFORCEMENT_POINT,
        }

        export_execution_artifacts(decision, result)
        return result
