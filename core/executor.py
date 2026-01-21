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


INVARIANT_ID = "ABE-EXEC-001"
ENFORCEMENT_POINT = "execution.commit"


configure()


@track(
    name=ENFORCEMENT_POINT,
    capture_input=True,
    capture_output=True,
)
def execute(decision: Decision) -> Dict[str, Any]:
    decision_id = decision.decision_id
    action = decision.proposal.action

    try:
        enforce_authority(decision)

        authority = decision.authority
        authority_overbroad = authority is not None and authority.scope is None

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

        export_execution_artifacts(decision, result)
        return result

    except AuthorityMissing as e:
        deny_reason = "missing_authority"
        message = str(e)

    except AuthorityExpired as e:
        deny_reason = "expired_authority"
        message = str(e)

    except AuthorityScopeViolation as e:
        deny_reason = "scope_violation"
        message = str(e)

    result = {
        "status": "blocked",
        "execution_allowed": False,
        "deny_reason": deny_reason,
        "message": message,
        "decision_id": decision_id,
        "action": action,
        "authority_overbroad": False,
        "invariant_id": INVARIANT_ID,
        "enforcement_point": ENFORCEMENT_POINT,
    }

    export_execution_artifacts(decision, result)
    return result
