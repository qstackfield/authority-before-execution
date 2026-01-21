from __future__ import annotations

import argparse
import json
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
    if not dt:
        return "—"
    return dt.isoformat().replace("+00:00", "Z")


def _safe_read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _hr(char: str = "─", width: int = 78) -> None:
    print(char * width)


def _print_kv(key: str, value: Any, width: int = 16) -> None:
    print(f"{key:<{width}}: {value}")


def _build_base_decision() -> Decision:
    proposal = Proposal(
        action="deploy_model",
        params={"model": "gpt-4.1", "environment": "production"},
        rationale="Deploy approved model version after validation pass",
    )
    return Decision(
        decision_id="demo-deploy-001",
        proposal=proposal,
        authority=None,
        created_at=_now_utc(),
    )


def _bind_authority(decision: Decision, ttl_seconds: int) -> Decision:
    auth = Authority(
        approved_by="security-lead@company.com",
        reason="Approved under incident protocol IR-2026-014",
        scope="deploy_model",
        expires_at=_now_utc() + timedelta(seconds=ttl_seconds),
    )
    return Decision(
        decision_id=decision.decision_id,
        proposal=decision.proposal,
        authority=auth,
        created_at=decision.created_at,
    )


def _attempt_line(n: int, decision: Decision, result: Dict[str, Any]) -> str:
    action = result.get("action") or decision.proposal.action
    allowed = bool(result.get("execution_allowed"))
    outcome = "PERMITTED" if allowed else "BLOCKED"
    deny = result.get("deny_reason") if not allowed else "—"

    auth = decision.authority
    if auth is None:
        auth_str = "NONE"
        scope_str = "—"
        exp_str = "—"
    else:
        auth_str = auth.approved_by
        scope_str = auth.scope if auth.scope is not None else "(overbroad)"
        exp_str = _fmt_ts(auth.expires_at)

    return (
        f"{n}) {decision.decision_id:<14}  "
        f"{action:<12}  "
        f"{outcome:<9}  "
        f"{deny:<16}  "
        f"{scope_str:<12}  "
        f"{exp_str}"
    )


def _artifact_summary(dir_path: Path) -> Dict[str, Any]:
    artifacts = sorted(dir_path.glob("*.json"))
    known = {
        "demo-deploy-001.json": dir_path / "demo-deploy-001.json",
        "demo-delete-001.json": dir_path / "demo-delete-001.json",
        "manifest.json": dir_path / "manifest.json",
    }

    present_known = {k: str(p) for k, p in known.items() if p.exists()}
    return {
        "count": len(artifacts),
        "known": present_known,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="demo.run_demo",
        description="Authority Before Execution - execution boundary proof",
    )
    parser.add_argument("--ttl", type=int, default=5, help="Authority TTL seconds (default: 5)")
    parser.add_argument("--wait", type=int, default=6, help="Wait seconds to ensure TTL expires (default: 6)")
    parser.add_argument(
        "--list-artifacts",
        action="store_true",
        help="List all artifact JSON paths (not recommended for video)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Reduce header verbosity for small screens",
    )
    args = parser.parse_args()

    run_id = str(uuid.uuid4())
    run_started_at = _now_utc()

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    if not args.compact:
        _hr("═")
        print("Authority Before Execution — Execution Boundary Proof")
        _hr("═")
        _print_kv("run_id", run_id)
        _print_kv("started_at", _fmt_ts(run_started_at))
        _print_kv("invariant_id", INVARIANT_ID)
        _print_kv("invariant", INVARIANT_STATEMENT)
        _hr()
    else:
        print("Authority Before Execution — Execution Boundary Proof")
        _print_kv("invariant_id", INVARIANT_ID)
        _hr()

    results: List[Dict[str, Any]] = []

    base = _build_base_decision()

    # 1) Missing authority
    r1 = execute(base)
    results.append(r1)

    # 2) Valid scoped authority
    authorized = _bind_authority(base, ttl_seconds=args.ttl)
    r2 = execute(authorized)
    results.append(r2)

    # 3) Scope violation
    destructive = Decision(
        decision_id="demo-delete-001",
        proposal=Proposal(
            action="delete_model",
            params={"model": "gpt-4.1", "environment": "production"},
            rationale="Attempted destructive action (must be blocked by scope)",
        ),
        authority=authorized.authority,
        created_at=_now_utc(),
    )
    r3 = execute(destructive)
    results.append(r3)

    # 4) Expired authority
    if args.wait > 0:
        time.sleep(args.wait)
    r4 = execute(authorized)
    results.append(r4)

    # Attempt table (low-scroll)
    print("Attempts")
    _hr()
    print(
        f"{'#':<2} {'decision_id':<14}  {'action':<12}  {'outcome':<9}  "
        f"{'deny_reason':<16}  {'scope':<12}  {'expires_at'}"
    )
    _hr()
    print(_attempt_line(1, base, r1))
    print(_attempt_line(2, authorized, r2))
    print(_attempt_line(3, destructive, r3))
    print(_attempt_line(4, authorized, r4))
    _hr()

    # Evaluation summary
    summary = evaluate_decision_runs(results)
    print("Evaluation Summary")
    _hr()
    print(json.dumps(summary, indent=2, sort_keys=True))
    log_decision_evaluation(summary)
    _hr()

    # Verdict
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

    # Artifacts: summary by default, full list only if requested
    a = _artifact_summary(ARTIFACT_DIR)
    print("Artifacts (local proof)")
    _hr()
    print(f"- {ARTIFACT_DIR}/ ({a['count']} JSON files)")
    for name, path in a["known"].items():
        print(f"- {name}: {path}")
        j = _safe_read_json(Path(path))
        if j and "timestamp" in j:
            print(f"  timestamp: {j['timestamp']}")
    if args.list_artifacts:
        _hr()
        for p in sorted(ARTIFACT_DIR.glob("*.json")):
            print(f"- {p}")
    _hr()
    print("Done.")


if __name__ == "__main__":
    main()
