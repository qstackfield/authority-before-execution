from datetime import datetime, timezone

from core.decision import Proposal, Decision
from core.executor import execute
from core.authority_bindings import bind_authority
from core.evaluation import evaluate_decision_runs


def run_experiment():
    results = []

    proposal = Proposal(
        action="deploy_model",
        params={"model": "gpt-4.1"},
        rationale="Routine model deployment",
    )

    # ── Ungoverned executions ──
    for i in range(3):
        decision = Decision(
            decision_id=f"ungoverned-{i}",
            proposal=proposal,
            authority=None,
            created_at=datetime.now(timezone.utc),
        )
        r = execute(decision)
        results.append(r)

    # ── Governed executions ──
    for i in range(3):
        decision = Decision(
            decision_id=f"governed-{i}",
            proposal=proposal,
            authority=None,
            created_at=datetime.now(timezone.utc),
        )

        decision = bind_authority(
            decision,
            approved_by="change-control@company.com",
            reason="Approved during scheduled change window",
            scope=["deploy_model"],
            ttl_seconds=30,
        )

        r = execute(decision)
        results.append(r)

    summary = evaluate_decision_runs(results)
    print("\n=== Comparative Experiment Summary ===\n")
    print(summary)


if __name__ == "__main__":
    run_experiment()
