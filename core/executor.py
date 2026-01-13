from core.authority_gate import enforce_authority, AuthorityMissing


class ExecutionFailed(Exception):
    pass


def execute(decision):
    """
    The only place where state change is allowed.
    If authority is missing or invalid, execution does not occur.
    """
    # HARD GATE - nothing happens before this
    enforce_authority(decision)

    # ---- EXECUTION BEGINS ----
    # This is intentionally minimal for the demo.
    # Any real side effect would live here.
    action = decision.get("action")
    params = decision.get("params", {})

    return {
        "status": "executed",
        "action": action,
        "params": params,
    }
