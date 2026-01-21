from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List


def _opik_track(name: str):
    try:
        from opik import track  # type: ignore
        return track(name=name)
    except Exception:
        def _noop(fn):
            return fn
        return _noop


def evaluate_decision_runs(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    allowed = 0
    denied = 0
    overbroad = 0

    deny_reasons = Counter()

    for r in results:
        if r.get("execution_allowed"):
            allowed += 1
        else:
            denied += 1
            deny_reasons[r.get("deny_reason", "unknown")] += 1

        if r.get("authority_overbroad"):
            overbroad += 1

    return {
        "total_attempts": total,
        "allowed": allowed,
        "denied": denied,
        "allow_rate": allowed / total if total else 0.0,
        "deny_breakdown": dict(deny_reasons),
        "overbroad_authority_used": overbroad,
    }


@_opik_track("decision.evaluation")
def log_decision_evaluation(summary: Dict[str, Any]) -> Dict[str, Any]:
    return summary
