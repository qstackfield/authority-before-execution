#!/usr/bin/env python3
"""
Authority Before Execution — Controlled Variance Demo (Demo A)

Invariant: ABE-EXEC-001
If explicit authority is not present, valid, and in scope at execution time,
the state transition must not occur.

What this demo proves:
- The invariant holds across MANY attempts (N)
- Under controlled, explainable variance (not fuzzing)
- With mixed authority states:
  - missing authority
  - valid scoped authority
  - scope violation
  - expired authority
  - overbroad authority (scope=None) — allowed, but governance-poor

Outputs:
- Deterministic console output (seeded)
- JSON artifacts written by the executor under docs/artifacts/ (runtime only; gitignored)
- Evaluation summary with allow/deny distribution

Run:
  python3 -m demo.run_variance --n 50 --seed 7
  python3 -m demo.run_variance --n 200 --seed 7 --quiet
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

from core.decision import Proposal, Authority, Decision
from core.executor import execute
from core.evaluation import evaluate_decision_runs, log_decision_evaluation


# ---------------------------------------------------------------------------
# Invariant (canonical, referenced everywhere)
# ---------------------------------------------------------------------------

INVARIANT_ID = "ABE-EXEC-001"
INVARIANT_TEXT = (
    "If explicit authority is not present, valid, and in scope at execution time, "
    "the state transition must not occur."
)

ACTIONS = ["deploy_model", "delete_model"]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def other_action(action: str) -> str:
    return "delete_model" if action == "deploy_model" else "deploy_model"


def normalize(value: Any, default: str = "-") -> str:
    """
    Console-safe normalization.
    Execution logic and artifacts remain authoritative.
    """
    if value is None:
        return default
    return str(value)


# ---------------------------------------------------------------------------
# Decision + Authority construction (no magic)
# ---------------------------------------------------------------------------

def build_decision(
    decision_id: str,
    action: str,
    authority: Authority | None,
) -> Decision:
    proposal = Proposal(
        action=action,
        params={"model": "gpt-4.1", "environment": "production"},
        rationale="Controlled variance evaluation of execution-time authority enforcement",
    )
    return Decision(
        decision_id=decision_id,
        proposal=proposal,
        authority=authority,
        created_at=utcnow(),
    )


def make_authority(scope: str | None, ttl_seconds: int, reason: str) -> Authority:
    return Authority(
        approved_by="security-lead@company.com",
        reason=reason,
        scope=scope,               # None => overbroad authority
        expires_at=utcnow() + timedelta(seconds=ttl_seconds),
    )


# ---------------------------------------------------------------------------
# Controlled variance generation
# ---------------------------------------------------------------------------

def generate_cases(n: int, seed: int) -> List[Tuple[str, str, Authority | None]]:
    """
    Deterministic, explainable variance.
    This is NOT fuzzing.

    Returns:
      List of (decision_id, action, authority)
    """
    rng = random.Random(seed)

    recipe: List[Tuple[str, float]] = [
        ("missing_authority", 0.35),
        ("valid_scoped", 0.30),
        ("scope_violation", 0.20),
        ("expired_authority", 0.10),
        ("overbroad_authority", 0.05),
    ]

    total = sum(w for _, w in recipe)
    recipe = [(name, w / total) for (name, w) in recipe]

    def pick_case() -> str:
        x = rng.random()
        acc = 0.0
        for name, w in recipe:
            acc += w
            if x <= acc:
                return name
        return recipe[-1][0]

    cases: List[Tuple[str, str, Authority | None]] = []

    for i in range(1, n + 1):
        decision_id = f"var-{i:03d}"
        action = rng.choice(ACTIONS)
        case = pick_case()

        if case == "missing_authority":
            auth = None

        elif case == "valid_scoped":
            auth = make_authority(
                scope=action,
                ttl_seconds=rng.randint(20, 90),
                reason="Approved for controlled variance run (scoped)",
            )

        elif case == "scope_violation":
            auth = make_authority(
                scope=other_action(action),
                ttl_seconds=rng.randint(20, 90),
                reason="Approved for controlled variance run (wrong scope)",
            )

        elif case == "expired_authority":
            auth = make_authority(
                scope=action,
                ttl_seconds=-5,  # expired on purpose
                reason="Approved for controlled variance run (expired)",
            )

        elif case == "overbroad_authority":
            auth = make_authority(
                scope=None,
                ttl_seconds=rng.randint(20, 90),
                reason="Approved for controlled variance run (overbroad)",
            )

        else:
            auth = None

        cases.append((decision_id, action, auth))

    return cases


def format_scope(auth: Authority | None) -> str:
    if auth is None:
        return "NONE"
    return normalize(auth.scope, default="NONE(scope)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Authority Before Execution — Controlled Variance Demo (Demo A)"
    )
    ap.add_argument("--n", type=int, default=50, help="Number of attempts")
    ap.add_argument("--seed", type=int, default=7, help="Deterministic run seed")
    ap.add_argument("--quiet", action="store_true", help="Print summary only")
    args = ap.parse_args()

    if args.n < 1:
        raise SystemExit("--n must be >= 1")

    print("\n" + "=" * 78)
    print("Authority Before Execution — Controlled Variance Demo")
    print("=" * 78)
    print(f"invariant_id : {INVARIANT_ID}")
    print(f"invariant    : {INVARIANT_TEXT}")
    print(f"attempts     : {args.n}")
    print(f"seed         : {args.seed}")

    results: List[Dict[str, Any]] = []
    cases = generate_cases(n=args.n, seed=args.seed)

    for decision_id, action, auth in cases:
        decision = build_decision(decision_id, action, auth)
        result = execute(decision)
        results.append(result)

        if not args.quiet:
            outcome = normalize(result.get("outcome"))
            deny = normalize(result.get("deny_reason"))
            scope = format_scope(auth)
            expires = normalize(auth.expires_at.isoformat() if auth else None)

            print(
                f"{decision_id}  "
                f"action={action:<11} "
                f"outcome={outcome:<9} "
                f"reason={deny:<18} "
                f"scope={scope:<14} "
                f"expires={expires}"
            )

    print("\n" + "=" * 78)
    print("Variance Evaluation Summary")
    print("=" * 78)

    summary = evaluate_decision_runs(results)
    print(json.dumps(summary, indent=2, sort_keys=True))
    log_decision_evaluation(summary)

    print("\nDone.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
