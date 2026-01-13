"""
executor.py

Execution boundary for authority-gated actions.

This is the only place where state change is allowed.
All execution outcomes are traced here (allow + deny).
"""

from opik import track, configure
from core.authority_gate import (
    enforce_authority,
    AuthorityMissing,
    AuthorityExpired,
    AuthorityScopeViolation,
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

    Returns a normalized outcome shape for both allow and deny so:
    - the demo can print consistently
    - Opik traces can be evaluated consistently
    """

    try:
        enforce_authority(decision)
        return {
            "status": "executed",
            "action": decision.get("action"),
            "params": decision.get("params"),
            "execution_allowed": True,
            "deny_reason": None,
        }

    except AuthorityMissing as e:
        return {
            "status": "blocked",
            "action": decision.get("action"),
            "params": decision.get("params"),
            "execution_allowed": False,
            "deny_reason": "missing_authority",
            "message": str(e),
        }

    except AuthorityExpired as e:
        return {
            "status": "blocked",
            "action": decision.get("action"),
            "params": decision.get("params"),
            "execution_allowed": False,
            "deny_reason": "expired_authority",
            "message": str(e),
        }

    except AuthorityScopeViolation as e:
        return {
            "status": "blocked",
            "action": decision.get("action"),
            "params": decision.get("params"),
            "execution_allowed": False,
            "deny_reason": "scope_violation",
            "message": str(e),
        }
