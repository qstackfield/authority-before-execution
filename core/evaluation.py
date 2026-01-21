from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

from core.observability_guard import trace_if_enabled


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


@trace_if_enabled("decision.evaluation")
def log_decision_evaluation(summary: Dict[str, Any]) -> Dict[str, Any]:
    return summary
