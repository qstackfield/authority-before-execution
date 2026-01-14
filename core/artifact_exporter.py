"""
artifact_exporter.py

Exports immutable execution artifacts at the execution boundary.

These artifacts are the concrete proof that:
- enforcement happened
- an invariant was applied
- execution either occurred or was blocked

Artifacts are not samples.
They are first-class governance evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from core.decision import Decision


# ──────────────────────────────────────────────────────────────────────────────
# Artifact configuration
# ──────────────────────────────────────────────────────────────────────────────

ARTIFACT_ROOT = Path("docs/artifacts")

INVARIANT_ID = "ABE-EXEC-001"
ENFORCEMENT_POINT = "execution.commit"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def export_execution_artifacts(
    decision: Decision,
    execution_result: Dict[str, Any],
) -> None:
    """
    Persist execution input + outcome as an immutable JSON artifact.

    This function MUST:
    - never raise
    - never affect execution semantics
    - always attempt best-effort persistence

    Artifacts are written only at the execution boundary.
    """

    try:
        ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

        decision_id = decision.decision_id

        authority_block: Optional[Dict[str, Any]] = None
        if decision.authority:
            authority_block = {
                "approved_by": decision.authority.approved_by,
                "scope": decision.authority.scope,
                "expires_at": (
                    decision.authority.expires_at.isoformat().replace("+00:00", "Z")
                    if decision.authority.expires_at
                    else None
                ),
            }

        artifact = {
            # ── Identity ──
            "decision_id": decision_id,
            "timestamp": _utcnow_iso(),

            # ── Enforcement metadata ──
            "invariant_id": INVARIANT_ID,
            "enforcement_point": ENFORCEMENT_POINT,

            # ── Outcome ──
            "execution_allowed": execution_result.get("execution_allowed"),
            "deny_reason": execution_result.get("deny_reason"),
            "authority_overbroad": execution_result.get("authority_overbroad"),

            # ── Decision input (what was attempted) ──
            "action": decision.proposal.action,
            "params": decision.proposal.params,

            # ── Authority context (what permitted or blocked it) ──
            "authority": authority_block,
        }

        artifact_path = ARTIFACT_ROOT / f"{decision_id}.json"

        with artifact_path.open("w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, sort_keys=True)

    except Exception:
        # Artifact export is observational only.
        # Governance enforcement must remain intact even if export fails.
        return
