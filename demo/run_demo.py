import time

from core.authority_bindings import bind_authority
from core.executor import execute
from core.evaluation import (
    evaluate_decision_runs,
    log_decision_evaluation,
)


def _print_result(result: dict) -> None:
    if result.get("execution_allowed"):
        print("Execution permitted.")
        print(result)
        return

    msg = result.get("message") or "Execution blocked."
    print(msg)


def main():
    results = []  # ← NEW: collect execution outcomes

    decision = {
        "decision_id": "demo-deploy-001",
        "action": "deploy_model",
        "params": {
            "model": "gpt-4.1",
            "environment": "production",
        },
    }

    print("\nAttempting execution without authority.\n")
    r = execute(decision)
    results.append(r)
    _print_result(r)

    print("\nBinding short-lived authority scoped to this action.\n")
    authorized_decision = bind_authority(
        decision,
        approved_by="security-lead@company.com",
        reason="Change approved under incident protocol IR-2026-014",
        scope=["deploy_model"],
        ttl_seconds=5,
    )

    print("Attempting execution with valid authority.\n")
    r = execute(authorized_decision)
    results.append(r)
    _print_result(r)

    print("\nAttempting execution with authority that does not cover the action.\n")
    out_of_scope = dict(authorized_decision)
    out_of_scope["action"] = "delete_model"
    r = execute(out_of_scope)
    results.append(r)
    _print_result(r)

    print("\nWaiting for authority to expire.\n")
    time.sleep(6)

    print("Attempting execution after authority expiration.\n")
    r = execute(authorized_decision)
    results.append(r)
    _print_result(r)

    # ── Decision-level evaluation (single event) ──
    print("\n=== Evaluation Summary (decision-level) ===\n")
    summary = evaluate_decision_runs(results)
    print(summary)

    log_decision_evaluation(summary)


if __name__ == "__main__":
    main()
