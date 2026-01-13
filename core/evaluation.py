"""
evaluation.py

Decision-level evaluation for authority-bound execution.

This file answers one question:
Does authority persist at execution time for a given decision_id?
"""

from collections import Counter
from typing import List, Dict

from opik import track


def evaluate_decision_runs(results: List[Dict]) -> Dict:
    """
    Evaluate multiple execution attempts for the same decision_id.

    Input: list of execution results returned by executor.execute()
    Output: aggregate metrics suitable for Opik logging or reporting
    """

    total = len(results)
    allowed = sum(1 for r in results if r.get("execution_allowed"))
    denied = total - allowed

    deny_reasons = Counter(
        r.get("deny_reason") for r in results if not r.get("execution_allowed")
    )

    return {
        "total_attempts": total,
        "allowed": allowed,
        "denied": denied,
        "allow_rate": allowed / total if total else 0.0,
        "deny_breakdown": dict(deny_reasons),
    }


@track(
    name="decision.evaluation",
    capture_input=True,
    capture_output=True,
)
def log_decision_evaluation(summary: Dict) -> Dict:
    """
    Log a decision-level evaluation artifact to Opik.

    This should be called once per decision_id,
    after all execution attempts are complete.
    """
    return summary
