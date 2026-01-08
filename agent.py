from opik import track

@track(name="agent.propose_action")
def propose_action(task: str):
    return {
        "action": "send_email",
        "params": {"to": "user@example.com"},
        "reason": f"Proposed action for task: {task}"
    }
