from core.authority_gate import enforce_authority, AuthorityMissing
from core.authority_bindings import bind_authority


def main():
    decision = {
        "action": "deploy_model",
        "params": {
            "model": "gpt-4.1",
            "environment": "production"
        }
    }

    print("Attempting execution without authority...")
    try:
        enforce_authority(decision)
    except AuthorityMissing as e:
        print(str(e))

    print("\nBinding authority...\n")

    authorized_decision = bind_authority(
        decision,
        approved_by="security-lead@company.com",
        reason="Change approved under incident protocol IR-2026-014"
    )

    print("Attempting execution with authority...")
    enforce_authority(authorized_decision)
    print("Execution permitted.")


if __name__ == "__main__":
    main()
