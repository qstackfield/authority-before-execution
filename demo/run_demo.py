from core.authority_bindings import bind_authority
from core.executor import execute
from core.authority_gate import AuthorityMissing, AuthorityExpired
import time


def main():
    decision = {
        "action": "deploy_model",
        "params": {
            "model": "gpt-4.1",
            "environment": "production",
        },
    }

    print("\n=== Attempt 1: No authority bound ===\n")

    try:
        execute(decision)
    except AuthorityMissing as e:
        print(f"BLOCKED → {e}")

    print("\n=== Binding authority (short-lived) ===\n")

    authorized_decision = bind_authority(
        decision,
        approved_by="security-lead@company.com",
        reason="Change approved under incident protocol IR-2026-014",
        scope=["deploy_model"],
        ttl_seconds=5,
    )

    print("=== Attempt 2: Authority present ===\n")

    try:
        result = execute(authorized_decision)
        print("EXECUTED →", result)
    except Exception as e:
        print("UNEXPECTED BLOCK →", e)

    print("\n=== Waiting for authority to expire ===\n")
    time.sleep(6)

    print("=== Attempt 3: Authority expired ===\n")

    try:
        execute(authorized_decision)
    except AuthorityExpired as e:
        print(f"BLOCKED → {e}")
    except AuthorityMissing as e:
        print(f"BLOCKED → {e}")


if __name__ == "__main__":
    main()
