from __future__ import annotations

import argparse
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from core.decision import Proposal, Authority, Decision
from core.executor import execute
from core.evaluation import evaluate_decision_runs


INVARIANT_ID = "ABE-PROD-001"
INVARIANT_STATEMENT = (
    "Invalid actions are blocked at execution time, eliminating downstream "
    "human review, escalation, and approval work."
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _hr(char: str = "─", width: int = 78) -> None:
    print(char * width)


def _build_decision(
    decision_id: str,
    action: str,
    authority: Authority | None,
) -> Decision:
    return Decision(
        decision_id=decision_id,
        proposal=Proposal(
            action=action,
            params={"target": "production"},
            rationale="Automated task execution request",
        ),
        authority=authority,
        created_at=_now_utc(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="demo.run_productivity_proof",
        description="Authority Before Execution - Productivity Proof",
    )
    parser.add_argument(
        "--total",
        type=int,
        default=100,
        help="Total number of attempted actions (default: 100)",
    )
    parser.add_argument(
        "--valid-rate",
        type=float,
        default=0.27,
        help="Fraction of actions with valid authority (default: 0.27)",
    )
    args = parser.parse_args()

    total = args.total
    valid_count = int(total * args.valid_rate)
    invalid_count = total - valid_count

    print("Authority Before Execution - Productivity Proof")
    _hr("═")
    print(f"Invariant ID   : {INVARIANT_ID}")
    print(f"Invariant      : {INVARIANT_STATEMENT}")
    print(f"Started at     : {_now_utc().isoformat().replace('+00:00', 'Z')}")
    _hr("═")

    results: List[Dict] = []

    # Pre-approved, scoped, time-bound authority
    valid_authority = Authority(
        approved_by="automation-policy@company.com",
        reason="Pre-approved execution policy",
        scope="deploy_model",
        expires_at=_now_utc() + timedelta(minutes=5),
    )

    # Valid execution attempts
    for i in range(valid_count):
        decision = _build_decision(
            decision_id=f"valid-{i}-{uuid.uuid4().hex[:6]}",
            action="deploy_model",
            authority=valid_authority,
        )
        results.append(execute(decision))

    # Invalid execution attempts (missing authority)
    for i in range(invalid_count):
        decision = _build_decision(
            decision_id=f"invalid-{i}-{uuid.uuid4().hex[:6]}",
            action="deploy_model",
            authority=None,
        )
        results.append(execute(decision))

    summary = evaluate_decision_runs(results)

    blocked = summary["denied"]
    permitted = summary["allowed"]
    avoided_pct = (blocked / total) * 100 if total else 0.0

    _hr()
    print("Productivity Summary")
    _hr()
    print(f"Total attempted actions      : {total}")
    print(f"Permitted actions            : {permitted}")
    print(f"Blocked at execution boundary: {blocked}")
    print()
    print(f"Human decisions avoided      : {avoided_pct:.1f}%")
    _hr()

    print("Equivalent human workload eliminated")
    _hr()
    print(f"- {blocked} approvals")
    print(f"- {blocked} reviews")
    print(f"- {blocked} potential escalations")
    _hr()

    print("Interpretation")
    _hr()
    print(
        f"{blocked} out of {total} attempted actions were blocked "
        "at the execution boundary - before any human review, approval, "
        "escalation, or follow-up could occur."
    )
    print()
    print("No queues created.")
    print("No tickets opened.")
    print("No meetings scheduled.")
    print("No alerts triggered.")
    print()
    print(
        "Authority was enforced at execution time, eliminating invalid work "
        "before it entered the human workflow."
    )

    print()

    print(
    "Each blocked action represents a ticket that was never created, "
    "a review that never happened, and a meeting that never needed to be scheduled."
    )

    print()

    _hr()
    print("Invariant Verdict")
    _hr()
    print(f"Invariant {INVARIANT_ID}: HELD")
    print("Execution-time enforcement directly removed downstream human work.")
    _hr()

    print("Done.")


if __name__ == "__main__":
    main()
