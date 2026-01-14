from __future__ import annotations

import json
from datetime import timedelta, timezone
from typing import List, Dict, Any

from core.decision import Proposal, Authority, Decision
from core.executor import execute
from core.evaluation import evaluate_decision_runs, log_decision_evaluation


def utcnow():
    from datetime import datetime
    return datetime.now(timezone.utc)


def build_base_decision(decision_id: str, action: str) -> Decision:
    return Decision(
        decision_id=decision_id,
        proposal=Proposal(
            action=action,
            params={"model": "gpt-4.1", "environment": "production"},
            rationale="Controlled variance evaluation of execution authority",
        ),
        authority=None,
        created_at=utcnow(),
    )


def bind_authority(
    decision: Decision,
    scope: str | None,
    ttl_seconds: int,
) -> Decision:
    auth = Authority(
        approved_by="security-lead@company.com",
        reason="Approved for controlled execution variance test",
        scope=scope,
        expires_at=utcnow() + timedelta(seconds=ttl_seconds),
    )
    return Decision(
        decision_id=decision.decision_id,
        proposal=decision.proposal,
        authority=auth,
        created_at=decision.created_at,
    )


def main() -> None:
    print("\n" + "=" * 78)
    print("Authority Before Execution — Controlled Variance Demo")
    print("=" * 78)

    results: List[Dict[str, Any]] = []

    # 1. No authority (baseline)
    d1 = build_base_decision("var-001", "deploy_model")
    results.append(execute(d1))

    # 2. No authority (repeat — determinism check)
    d2 = build_base_decision("var-002", "deploy_model")
    results.append(execute(d2))

    # 3. Valid authority, correct scope
    d3 = bind_authority(
        build_base_decision("var-003", "deploy_model"),
        scope="deploy_model",
        ttl_seconds=30,
    )
    results.append(execute(d3))

    # 4. Valid authority, wrong scope
    d4 = bind_authority(
        build_base_decision("var-004", "delete_model"),
        scope="deploy_model",
        ttl_seconds=30,
    )
    results.append(execute(d4))

    # 5. Authority reused for different action
    reused_auth = d3.authority
    d5 = Decision(
        decision_id="var-005",
        proposal=Proposal(
            action="delete_model",
            params={"model": "gpt-4.1"},
            rationale="Reuse authority for unintended action",
        ),
        authority=reused_auth,
        created_at=utcnow(),
    )
    results.append(execute(d5))

    # 6. Expired authority
    d6 = bind_authority(
        build_base_decision("var-006", "deploy_model"),
        scope="deploy_model",
        ttl_seconds=1,
    )
    import time
    time.sleep(2)
    results.append(execute(d6))

    # 7. Overbroad authority (no scope)
    d7 = bind_authority(
        build_base_decision("var-007", "deploy_model"),
        scope=None,
        ttl_seconds=30,
    )
    results.append(execute(d7))

    print("\n" + "=" * 78)
    print("Variance Evaluation Summary")
    print("=" * 78)

    summary = evaluate_decision_runs(results)
    print(json.dumps(summary, indent=2, sort_keys=True))
    log_decision_evaluation(summary)

    print("\nDone.\n")


if __name__ == "__main__":
    main()
