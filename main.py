from opik import configure, track
from agent import propose_action

# Initialize Opik (uses COMET_* env vars)
configure()


@track(name="authority_before_execution.proof_of_life")
def proof_of_life():
    return {
        "status": "ok",
        "principle": "authority before execution"
    }


if __name__ == "__main__":
    # Step 1: proof of life
    print(proof_of_life())

    # Step 2: agent proposal (intent only, no execution)
    print(propose_action("Follow up with customer"))
