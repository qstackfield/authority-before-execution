"""
evaluation.py

Decision-level evaluation for authority-gated execution.

This module aggregates execution outcomes across multiple attempts
to make governance behavior measurable instead of anecdotal.
"""

from collections import Counter
from typing import List, Dict

from opik import track


def evaluate_decision_runs(results: List[Dict]) -> Dict:
    """
    Aggregate execution outcomes across multiple attempts.

    Expected input: list of results returned by executor.execute()
    """

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


@track(
    name="decision.evaluation",
    capture_input=True,
    capture_output=True,
)
def log_decision_evaluation(summary: Dict) -> Dict:
    """
    Emit a single evaluation artifact per experiment or decision batch.
    """
    return summary
