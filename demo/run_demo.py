from core.authority_bindings import bind_authority
from core.executor import execute
from core.authority_gate import (
    AuthorityMissing,
    AuthorityExpired,
    AuthorityScopeViolation,
)
import time


def main():
    decision = {
        "action": "deploy_model",
        "params": {
            "model": "gpt-4.1",
            "environment": "production"
        }
    }

    print("\nAttempting execution without authority.\n")

    try:
        execute(decision)
    except AuthorityMissing as e:
        print(e)

    print("\nBinding short-lived authority scoped to this action.\n")

    authorized_decision = bind_authority(
        decision,
        approved_by="security-lead@company.com",
        reason="Approved under incident protocol IR-2026-014",
        scope=["deploy_model"],
        ttl_seconds=5,
    )

    print("Attempting execution with valid authority.\n")

    try:
        result = execute(authorized_decision)
        print("Execution permitted.")
        print(result)
    except Exception as e:
        print("Execution blocked unexpectedly:", e)

    print("\nAttempting execution with authority that does not cover the action.\n")

    unauthorized_action = {
        "action": "delete_model",
        "params": {"model": "gpt-4.1"},
        "authority": authorized_decision["authority"],
    }

    try:
        execute(unauthorized_action)
    except AuthorityScopeViolation as e:
        print(e)

    print("\nWaiting for authority to expire.\n")
    time.sleep(5)

    print("Attempting execution after authority expiration.\n")

    try:
        execute(authorized_decision)
    except AuthorityExpired as e:
        print(e)


if __name__ == "__main__":
    main()
