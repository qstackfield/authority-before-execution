from __future__ import annotations

from typing import Any, Dict

from core.decision import Decision
from core.authority_gate import (
    enforce_authority,
    AuthorityMissing,
    AuthorityExpired,
    AuthorityScopeViolation,
    decision_snapshot,
)
from core.artifact_exporter import export_execution_artifacts

INVARIANT_ID = "ABE-EXEC-001"
ENFORCEMENT_POINT = "execution.commit"


def _track_if_available(fn):
    """
    Apply Opik tracing if installed.
    Execution must never depend on observability.
    """
    try:
        from opik import track  # type: ignore

        return track(
            name=ENFORCEMENT_POINT,
            capture_input=True,
            capture_output=True,
        )(fn)
    except Exception:
        return fn


@_track_if_available
def execute(decision: Decision) -> Dict[str, Any]:
    decision_id = decision.decision_id
    action = decision.proposal.action

    try:
        enforce_authority(decision)

        authority = decision.authority
        authority_overbroad = bool(authority and authority.scope is None)

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
