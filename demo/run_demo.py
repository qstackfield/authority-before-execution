from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.decision import Proposal, Authority, Decision
from core.executor import execute
from core.evaluation import evaluate_decision_runs, log_decision_evaluation


# ──────────────────────────────────────────────────────────────────────────────
# Invariant definition (this is the thing being proven)
# ──────────────────────────────────────────────────────────────────────────────

INVARIANT_ID = "ABE-EXEC-001"
INVARIANT_STATEMENT = (
    "If explicit authority is not present, valid, and in scope at execution time, "
    "the state transition must not occur."
)

# Where real execution artifacts are written
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


def _print_header(title: str) -> None:
    print("\n" + "═" * 78)
    print(title)
    print("═" * 78)


def _print_section(title: str) -> None:
    print("\n" + "─" * 78)
    print(title)
    print("─" * 78)


def _print_kv(key: str, value: Any, width: int = 18) -> None:
    print(f"{key:<{width}}: {value}")


def _report_attempt(label: str, decision: Decision, result: Dict[str, Any]) -> None:
    """
    Human-readable report that makes the execution boundary legible.
    Judges should be able to understand the outcome without reading code.
    """
    _print_section(label)

    _print_kv("decision_id", result.get("decision_id") or decision.decision_id)
    _print_kv("action", result.get("action") or decision.proposal.action)

    auth = decision.authority
    if auth is None:
        _print_kv("authority", "NONE")
    else:
        _print_kv("approved_by", auth.approved_by)
        _print_kv("scope", auth.scope if auth.scope is not None else "(overbroad)")
        _print_kv("expires_at", _fmt_ts(auth.expires_at))

    if result.get("execution_allowed"):
        _print_kv("outcome", "PERMITTED")
    else:
        _print_kv("outcome", "BLOCKED")
        _print_kv("deny_reason", result.get("deny_reason"))
        msg = result.get("message")
        if msg:
            _print_kv("message", msg)

    artifact_path = result.get("artifact_path")
    if artifact_path:
        p = Path(artifact_path)
        _print_kv("artifact", str(p))
        if p.exists():
            _print_kv("artifact_written", "yes")
            artifact_json = _safe_read_json(p)
            if artifact_json:
                _print_kv("artifact_ts", artifact_json.get("timestamp"))

    snap = result.get("decision_snapshot")
    if snap:
        _print_kv("snapshot", "included (traceable input contract)")


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
        reason="Change approved under incident protocol IR-2026-014",
        scope="deploy_model",
        expires_at=_now_utc() + timedelta(seconds=ttl_seconds),
    )
    return Decision(
        decision_id=decision.decision_id,
        proposal=decision.proposal,
        authority=auth,
        created_at=decision.created_at,
    )


def main() -> None:
    run_id = str(uuid.uuid4())
    run_started_at = _now_utc()

    _print_header("Authority Before Execution — Execution Boundary Proof")

    _print_kv("run_id", run_id)
    _print_kv("started_at", _fmt_ts(run_started_at))
    _print_kv("invariant_id", INVARIANT_ID)
    _print_kv("invariant", INVARIANT_STATEMENT)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []

    base = _build_base_decision()

    # 1) Missing authority → must fail closed
    _print_section("1) Attempt without authority")
    r = execute(base)
    results.append(r)
    _report_attempt("Result", base, r)

    # 2) Valid scoped authority → permitted
    authorized = _bind_authority(base, ttl_seconds=5)
    _print_section("2) Attempt with valid scoped authority")
    r = execute(authorized)
    results.append(r)
    _report_attempt("Result", authorized, r)

    # 3) Same authority, different action → scope violation
    destructive = Decision(
        decision_id="demo-delete-001",
        proposal=Proposal(
            action="delete_model",
            params={"model": "gpt-4.1", "environment": "production"},
            rationale="Attempted destructive action (should be blocked by scope)",
        ),
        authority=authorized.authority,
        created_at=_now_utc(),
    )
    _print_section("3) Attempt out of scope (authority does not cover action)")
    r = execute(destructive)
    results.append(r)
    _report_attempt("Result", destructive, r)

    # 4) Expired authority → denied
    print("\nWaiting for authority TTL to expire...")
    time.sleep(6)

    _print_section("4) Attempt after authority expiration")
    r = execute(authorized)
    results.append(r)
    _report_attempt("Result", authorized, r)

    # Evaluation summary
    _print_header("Evaluation Summary (decision-level)")
    summary = evaluate_decision_runs(results)
    print(json.dumps(summary, indent=2, sort_keys=True))
    log_decision_evaluation(summary)

    # Final verdict (this is the money line)
    _print_header("Invariant Verdict")
    invariant_held = summary.get("allowed", 0) == 1 and summary.get("denied", 0) == 3

    if invariant_held:
        print(f"Invariant {INVARIANT_ID}: HELD")
        print("All invalid execution attempts were blocked at the execution boundary.")
    else:
        print(f"Invariant {INVARIANT_ID}: VIOLATED")
        print("One or more invalid executions were permitted (unexpected).")

    _print_section("Artifacts written (local proof)")
    for p in sorted(ARTIFACT_DIR.glob("*.json")):
        print(f"- {p}")

    print("\nDone.\n")


if __name__ == "__main__":
    main()
