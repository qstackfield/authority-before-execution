"""
executor.py

Execution boundary for authority-gated actions.

This is the only place where state change is allowed.
All executions are traced.
"""

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

    All authority enforcement happens here.
    Outcome is reflected in trace + return value.
    """

    enforce_authority(decision)

    return {
        "status": "executed",
        "action": decision.get("action"),
        "params": decision.get("params"),
    }
