from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from core.decision import Proposal, Authority, Decision
from core.executor import execute
from core.evaluation import evaluate_decision_runs

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _print_header(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def _print_section(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def _attempt(label: str, decision: Decision, results: List[Dict[str, Any]]) -> None:
    _print_section(label)
    r = execute(decision)
    results.append(r)

    print(f"decision_id : {decision.decision_id}")
    print(f"action      : {decision.proposal.action}")
    print(f"outcome     : {'PERMITTED' if r['execution_allowed'] else 'BLOCKED'}")

    if not r["execution_allowed"]:
        print(f"reason      : {r.get('deny_reason')}")
        print(f"message     : {r.get('message')}")

    if r.get("decision_snapshot"):
        print("snapshot    : included (traceable execution input)")


def main() -> None:
    _print_header("Authority Before Execution — Authority Drift Demo")

    results: List[Dict[str, Any]] = []

    # ── Base proposal ───────────────────────────────────────────────────────
    proposal = Proposal(
        action="deploy_model",
        params={"model": "gpt-4.1", "environment": "production"},
        rationale="Deploy approved model version",
    )

    # ── Issue authority (short TTL) ─────────────────────────────────────────
    authority = Authority(
        approved_by="change-manager@company.com",
        reason="Approved during maintenance window",
        scope="deploy_model",
        expires_at=_now_utc() + timedelta(seconds=5),
    )

    decision = Decision(
        decision_id="drift-001",
        proposal=proposal,
        authority=authority,
        created_at=_now_utc(),
    )

    # ── Attempt 1: Valid execution ──────────────────────────────────────────
    _attempt(
        "1) Initial execution with valid authority",
        decision,
        results,
    )

    # ── Wait for authority to expire ────────────────────────────────────────
    print("\nWaiting for authority to expire...\n")
    time.sleep(6)

    # ── Attempt 2: Replay with expired authority ────────────────────────────
    replay = Decision(
        decision_id="drift-002",
        proposal=proposal,
        authority=authority,  # same authority reused
        created_at=_now_utc(),
    )

    _attempt(
        "2) Replay attempt using expired authority",
        replay,
        results,
    )

    # ── Evaluation summary ──────────────────────────────────────────────────
    _print_header("Authority Drift Evaluation Summary")
    summary = evaluate_decision_runs(results)
    print(json.dumps(summary, indent=2, sort_keys=True))

    print("\nKey takeaway:")
    print(
        "Authority reuse without revalidation is blocked. "
        "Execution-time enforcement prevents replay and drift."
    )

    print("\nDone.\n")


if __name__ == "__main__":
    main()
