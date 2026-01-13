import time

from core.authority_bindings import bind_authority
from core.executor import execute


def _print_result(result: dict) -> None:
    if result.get("execution_allowed"):
        print("Execution permitted.")
        print(result)
        return

    # Deny path
    msg = result.get("message") or "Execution blocked."
    print(msg)


def main():
    decision = {
        "action": "deploy_model",
        "params": {"model": "gpt-4.1", "environment": "production"},
    }

    print("\nAttempting execution without authority.\n")
    _print_result(execute(decision))

    print("\nBinding short-lived authority scoped to this action.\n")
    authorized_decision = bind_authority(
        decision,
        approved_by="security-lead@company.com",
        reason="Change approved under incident protocol IR-2026-014",
        scope=["deploy_model"],
        ttl_seconds=5,
    )

    print("Attempting execution with valid authority.\n")
    _print_result(execute(authorized_decision))

    print("\nAttempting execution with authority that does not cover the action.\n")
    out_of_scope = dict(authorized_decision)
    out_of_scope["action"] = "delete_model"
    _print_result(execute(out_of_scope))

    print("\nWaiting for authority to expire.\n")
    time.sleep(6)

    print("Attempting execution after authority expiration.\n")
    _print_result(execute(authorized_decision))


if __name__ == "__main__":
    main()
