"""
Experiment: Authority-Gated vs Ungoverned Execution

Hypothesis:
Decisions without explicit authority will be blocked at execution time.
Introducing scoped, time-bound authority will increase allowed execution
without permitting out-of-scope or expired actions.

Metrics:
- allow_rate
- deny_reason distribution
- authority misuse detection
"""

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
        results.append(execute(decision))

    # ── Governed executions (scoped) ──
    for i in range(2):
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

        results.append(execute(decision))

    # ── Over-broad authority execution ──
    decision = Decision(
        decision_id="overbroad-0",
        proposal=proposal,
        authority=None,
        created_at=datetime.now(timezone.utc),
    )

    decision = bind_authority(
        decision,
        approved_by="incident-commander@company.com",
        reason="Emergency approval without scoped restriction",
        scope=None,  # intentionally permissive
        ttl_seconds=30,
    )

    results.append(execute(decision))

    summary = evaluate_decision_runs(results)

    print("\n=== Comparative Experiment Summary ===\n")
    print(summary)


if __name__ == "__main__":
    run_experiment()
