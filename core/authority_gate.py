"""
authority_gate.py

Enforces a single invariant:

    No action may execute unless explicit authority
    is present, valid, and in scope at execution time.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable

from core.decision import Authority, Decision


class AuthorityMissing(Exception):
    pass


class AuthorityExpired(Exception):
    pass


class AuthorityScopeViolation(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _scope_allows_action(scope: Iterable[str] | None, action: str) -> bool:
    """
    Returns True if the authority scope allows the action.

    Scope semantics:
      - None      → no restriction (explicitly allowed)
      - iterable  → action must be present
    """
    if scope is None:
        return True

    return action in scope


def enforce_authority(decision: Decision) -> None:
    """
    Fail-closed authority enforcement.

    Raises a specific exception for each deny condition.
    """
    authority: Authority | None = decision.authority
    if authority is None:
        raise AuthorityMissing("Execution blocked: authority not bound")

    if not authority.approved_by:
        raise AuthorityMissing("Execution blocked: authority missing approver")

    if not authority.reason:
        raise AuthorityMissing("Execution blocked: authority missing justification")

    now = _utcnow()
    if authority.is_expired(now):
        raise AuthorityExpired("Execution blocked: authority expired")

    action = decision.proposal.action
    if not _scope_allows_action(authority.scope, action):
        raise AuthorityScopeViolation("Execution blocked: authority out of scope")


def decision_snapshot(decision: Decision) -> dict:
    """
    Stable, serializable snapshot for tracing and evaluation layers.

    Keeps the execution core strongly typed while allowing
    logging as a plain dictionary.
    """
    d = asdict(decision)

    d["created_at"] = decision.created_at.isoformat()

    if decision.authority and decision.authority.expires_at:
        d["authority"]["expires_at"] = decision.authority.expires_at.isoformat()

    return d
