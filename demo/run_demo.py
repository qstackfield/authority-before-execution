from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.decision import Proposal, Authority, Decision
from core.executor import execute
from core.evaluation import evaluate_decision_runs, log_decision_evaluation

INVARIANT_ID = "ABE-EXEC-001"
INVARIANT_STATEMENT = (
    "If explicit authority is not present, valid, and in scope at execution time, "
    "the state transition must not occur."
)

ARTIFACT_DIR = Path("docs/artifacts")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _fmt_ts(dt: Optional[datetime]) -> str:
    return "—" if not dt else dt.isoformat().replace("+00:00", "Z")


def _hr(char: str = "─", width: int = 78) -> None:
    print(char * width)


def _print_kv(key: str, value: Any, width: int = 16) -> None:
    print(f"{key:<{width}}: {value}")


def _set_opik_opt_in(enabled: bool) -> None:
    """
    Canonical opt-in toggle for Opik.
    - Default is OFF.
    - Only enabled when --opik is passed.
    """
    if enabled:
        os.environ["ABE_ENABLE_OPIK"] = "1"


def _clean_artifacts_dir() -> None:
    """
    Keep judge runs unambiguous.
    Remove stale JSON artifacts so every run produces a clean evidence set.
    """
    if not ARTIFACT_DIR.exists():
        return
    for f in ARTIFACT_DIR.glob("*.json"):
        try:
            f.unlink()
        except Exception:
            # Never block the demo due to filesystem edge cases
            pass


def _build_base_decision() -> Decision:
    return Decision(
        decision_id="demo-deploy-001",
        proposal=Proposal(
            action="deploy_model",
            params={"model": "gpt-4.1", "environment": "production"},
            rationale="Deploy approved model version after validation pass",
        ),
        authority=None,
        created_at=_now_utc(),
    )


def _bind_authority(decision: Decision, ttl: int) -> Decision:
    auth = Authority(
        approved_by="security-lead@company.com",
        reason="Approved under incident protocol IR-2026-014",
        scope="deploy_model",
        expires_at=_now_utc() + timedelta(seconds=ttl),
    )
    return Decision(
        decision_id=decision.decision_id,
        proposal=decision.proposal,
        authority=auth,
        created_at=decision.created_at,
    )


def _attempt_row(n: int, decision: Decision, result: Dict[str, Any]) -> str:
    outcome = "PERMITTED" if result.get("execution_allowed") else "BLOCKED"
    deny = result.get("deny_reason") or "—"
    scope = decision.authority.scope if decision.authority else "—"
    exp = _fmt_ts(decision.authority.expires_at) if decision.authority else "—"
    action = result.get("action") or decision.proposal.action

    return (
        f"{n}) {decision.decision_id:<14}  "
        f"{action:<12}  "
        f"{outcome:<9}  "
        f"{deny:<16}  "
        f"{scope:<12}  "
        f"{exp}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="demo.run_demo",
        description="Authority Before Execution — Execution Boundary Proof",
    )
    parser.add_argument("--ttl", type=int, default=5, help="Authority TTL seconds (default: 5)")
    parser.add_argument("--wait", type=int, default=6, help="Seconds to wait so TTL expires (default: 6)")
    parser.add_argument("--compact", action="store_true", help="Reduce header verbosity")
    parser.add_argument("--opik", action="store_true", help="OPT-IN: enable Opik boundary tracing")
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Do not clean docs/artifacts/*.json before running (default: clean)",
    )
    args = parser.parse_args()

    # Optional observability is opt-in only.
    _set_opik_opt_in(args.opik)

    # Judge-first evidence: ensure artifacts are not mixed across runs.
    if not args.keep_artifacts:
        _clean_artifacts_dir()

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    run_id = str(uuid.uuid4())
    started_at = _now_utc()

    _hr("═")
    print("Authority Before Execution - Execution Boundary Proof")
    _hr("═")
    _print_kv("run_id", run_id)
    if not args.compact:
        _print_kv("started_at", _fmt_ts(started_at))
    _print_kv("invariant_id", INVARIANT_ID)
    _print_kv("invariant", INVARIANT_STATEMENT)
    _hr()

    results: List[Dict[str, Any]] = []

    base = _build_base_decision()

    # 1) Missing authority -> BLOCKED
    results.append(execute(base))

    # 2) Valid scoped authority -> PERMITTED
    authorized = _bind_authority(base, args.ttl)
    results.append(execute(authorized))

    # 3) Scope violation -> BLOCKED
    destructive = Decision(
        decision_id="demo-delete-001",
        proposal=Proposal(
            action="delete_model",
            params={"model": "gpt-4.1", "environment": "production"},
            rationale="Destructive action (must be blocked by scope)",
        ),
        authority=authorized.authority,
        created_at=_now_utc(),
    )
    results.append(execute(destructive))

    # 4) Expired authority -> BLOCKED
    if args.wait > 0:
        time.sleep(args.wait)
    results.append(execute(authorized))

    print("Attempts")
    _hr()
    print(
        f"{'#':<2} {'decision_id':<14}  {'action':<12}  "
        f"{'outcome':<9}  {'deny_reason':<16}  {'scope':<12}  expires_at"
    )
    _hr()
    for i, (d, r) in enumerate(zip([base, authorized, destructive, authorized], results), 1):
        print(_attempt_row(i, d, r))
    _hr()

    summary = evaluate_decision_runs(results)
    print("Evaluation Summary")
    _hr()
    print(json.dumps(summary, indent=2, sort_keys=True))
    log_decision_evaluation(summary)
    _hr()

    invariant_held = (summary.get("allowed", 0) == 1) and (summary.get("denied", 0) == 3)

    print("Invariant Verdict")
    _hr()
    if invariant_held:
        print(f"Invariant {INVARIANT_ID}: HELD")
        print("All invalid execution attempts were blocked at the execution boundary.")
    else:
        print(f"Invariant {INVARIANT_ID}: VIOLATED")
        print("One or more invalid executions were permitted (unexpected).")
    _hr()

    json_count = len(list(ARTIFACT_DIR.glob("*.json")))
    print(f"Artifacts written: {json_count} JSON files")
    print("Done.")


if __name__ == "__main__":
    main()
