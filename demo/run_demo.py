from datetime import datetime, timedelta
import time

from core.decision import Proposal, Authority, Decision
from core.authority_bindings import bind_authority
from core.executor import execute
from core.evaluation import evaluate_decision_runs, log_decision_evaluation


def _print_result(result: dict) -> None:
    if result.get("execution_allowed"):
        print("Execution permitted.")
    else:
        print(result.get("message", "Execution blocked."))


def main():
    results = []

    proposal = Proposal(
        action="deploy_model",
        params={
            "model": "gpt-4.1",
            "environment": "production",
        },
        rationale="Deploy approved model version after validation pass",
    )

    decision = Decision(
        decision_id="demo-deploy-001",
        proposal=proposal,
        authority=None,
        created_at=datetime.utcnow(),
    )

    print("\nAttempting execution without authority.\n")
    r = execute(decision)
    results.append(r)
    _print_result(r)

    print("\nBinding short-lived authority scoped to this action.\n")
    authority = Authority(
        approved_by="security-lead@company.com",
        reason="Change approved under incident protocol IR-2026-014",
        scope="deploy_model",
        expires_at=datetime.utcnow() + timedelta(seconds=5),
    )

    authorized_decision = Decision(
        decision_id=decision.decision_id,
        proposal=proposal,
        authority=authority,
        created_at=decision.created_at,
    )

    print("Attempting execution with valid authority.\n")
    r = execute(authorized_decision)
    results.append(r)
    _print_result(r)

    print("\nAttempting execution with authority that does not cover the action.\n")
    out_of_scope_proposal = Proposal(
        action="delete_model",
        params=proposal.params,
        rationale="Attempted destructive action",
    )

    out_of_scope_decision = Decision(
        decision_id="demo-delete-001",
        proposal=out_of_scope_proposal,
        authority=authority,
        created_at=datetime.utcnow(),
    )

    r = execute(out_of_scope_decision)
    results.append(r)
    _print_result(r)

    print("\nWaiting for authority to expire.\n")
    time.sleep(6)

    print("Attempting execution after authority expiration.\n")
    r = execute(authorized_decision)
    results.append(r)
    _print_result(r)

    print("\n=== Evaluation Summary (decision-level) ===\n")
    summary = evaluate_decision_runs(results)
    print(summary)

    log_decision_evaluation(summary)


if __name__ == "__main__":
    main()
