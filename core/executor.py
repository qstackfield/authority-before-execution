"""
executor.py

Execution boundary for authority-gated actions.

This is the only place where state change is allowed.
All executions are traced with explicit outcomes and reasons.
"""

from datetime import datetime
from opik import track, configure

from core.authority_gate import (
    enforce_authority,
    AuthorityMissing,
    AuthorityExpired,
)

# Initialize Opik using existing config / env vars
configure()


@track(
    name="execution.commit",
    capture_input=True,
    capture_output=True,
)
def execute(decision: dict) -> dict:
    """
    Execute a decision only if authority is valid at runtime.
    """

    action = decision.get("action")
    authority = decision.get("authority")

    trace_context = {
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        enforce_authority(decision)

        # Successful execution
        result = {
            "status": "executed",
            "action": action,
            "params": decision.get("params"),
        }

        trace_context.update({
            "execution_result": "executed",
            "approved_by": authority.get("approved_by") if authority else None,
            "scope": authority.get("scope") if authority else None,
            "expires_at": authority.get("expires_at") if authority else None,
        })

        return result

    except AuthorityMissing as e:
        trace_context.update({
            "execution_result": "blocked",
            "denial_reason": "missing_authority",
        })
        raise

    except AuthorityExpired as e:
        trace_context.update({
            "execution_result": "blocked",
            "denial_reason": "expired_authority",
        })
        raise

    except Exception as e:
        trace_context.update({
            "execution_result": "blocked",
            "denial_reason": "unknown_error",
        })
        raise
