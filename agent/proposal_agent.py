def propose_action() -> dict:
    """
    Propose an action without binding authority.

    This is intentional. The agent can reason,
    but it cannot approve its own execution.
    """
    return {
        "action": "send_email",
        "params": {
            "to": "user@example.com"
        }
    }
