# Authority Before Execution

## Evaluation-First Governance for Autonomous Agents

Authority Before Execution is a minimal control plane for autonomous agents where **execution is impossible without explicit, runtime authority**.

The system enforces one invariant:

> **If authority is not present, valid, and in scope at execution time, the state transition does not occur.**

Agents may reason, plan, and propose actions freely.  
They are **not allowed to commit state changes** unless authority is bound at the moment of execution.

This repository is intentionally small. It is designed to be judged quickly: enforcement boundary, artifacts, evaluation, and traces.

---

## The Invariant

**Invariant ID:** ABE-EXEC-001

**Invariant statement:**  
If explicit authority is not present, valid, and in scope **at execution time**, the state transition must not occur.

**What makes this real:**
- Enforcement happens at a single execution boundary (the commit point).
- Outcomes are returned as structured results (no “best effort”, no caller discretion).
- Every attempt writes an immutable JSON execution artifact.
- Opik traces capture boundary behavior and evaluation summaries.

---

## Quick Proof (Run This First)

Run the baseline proof:

    python3 -m demo.run_demo

What you should see:
1. Attempt without authority → **blocked** (fail closed)
2. Attempt with valid scoped authority → **permitted**
3. Attempt out of scope → **blocked**
4. Attempt after expiration → **blocked**
5. Evaluation summary printed at the end
6. JSON artifacts written under:

    docs/artifacts/

Artifacts are generated at runtime and include:
- decision_id
- timestamp
- action
- authority context (issuer, scope, expires_at)
- execution_allowed (true/false)
- deny_reason (if blocked)

This is enforcement proof, not narrative.

---

## Demo Suite (Four Proofs, Four Failure Modes)

These demos build on the same invariant and execution boundary. Each isolates a different governance risk.

### Demo A - Controlled Variance (distribution proof)

    python3 -m demo.run_variance

Purpose:
- Same invariant
- Many attempts
- Mixed scopes and TTLs
- Produces deny distributions and overbroad usage detection

What judges should take away:
- Denials are deterministic and categorized
- Authority quality becomes measurable (not just “success rate”)

---

### Demo B - Prompt Injection Mapped to Authority (escalation proof)

    python3 -m demo.run_prompt_injection

Purpose:
- Demonstrate why prompt content is not enough to cause state change
- Injection attempts to escalate scope or action
- Authority gate blocks escalation at execution time

What judges should take away:
- Prompt injection fails when authority is enforced at execution time
- “Reasoning” cannot create permissions the system does not grant

---

### Demo C - Authority Drift / Replay Prevention (revalidation proof)

    python3 -m demo.run_authority_drift

Purpose:
- Show that approvals cannot be reused indefinitely
- A valid approval becomes invalid after expiry
- Replay attempt is blocked deterministically

What judges should take away:
- Execution-time enforcement prevents replay and drift
- “Approval happened earlier” is not sufficient

---

### Demo D - Comparative Agent Outcomes (delta proof)

    python3 -m demo.run_comparative_agent

Purpose:
- Same agent, same prompts, two modes:
  - Mode 1: no authority bound at execution time
  - Mode 2: authority bound at execution time

What judges should take away:
- The execution boundary stays constant
- Only execution-time authority determines what becomes real
- You can quantify the delta with evaluation summaries and artifacts

---

## Architecture (High Level)

User Task  
↓  
Agent (Reasoning + Proposal)  
↓  
Evaluation + Trace (Opik)  
↓  
Execution Boundary (commit point)  
↓  
Authority Gate (runtime enforcement)

Approved → Execute → Outcome Traced  
Denied → Block → Denial Traced  

**No valid authority → no state change.**

---

## Where Enforcement Happens (The Only Commit Point)

The execution boundary is explicit:

- `core/executor.py` is the only place state-changing execution is permitted.
- `core/authority_gate.py` enforces authority at runtime:
  - missing authority → deny
  - expired authority → deny
  - out of scope → deny
- `core/artifact_exporter.py` writes immutable JSON artifacts for every attempt.
- `core/evaluation.py` computes decision-level metrics (allow rate, deny breakdown, overbroad usage).
- Opik traces capture boundary behavior and evaluation summaries.

This is the point: governance is enforced at the commit boundary, not reconstructed after the fact.

---

## Evaluation and Observability

Opik is used as an evaluation substrate, not as a logging sink.

Tracked and evaluated signals include:
- allow / deny rates
- deny reasons (missing, expired, scope violation)
- overbroad authority usage
- comparative outcomes across runs

This allows teams to separate:
- execution success
from
- governance quality

An execution can succeed and still be governance-poor.  
That distinction is measurable here.

---

## Non-Goals (On Purpose)

This project intentionally does not attempt to solve:
- identity and RBAC
- approval workflow UI
- policy DSLs
- credential storage / key management
- multi-agent orchestration frameworks
- production deployment patterns

Those problems matter, but they are orthogonal to proving the invariant.

The goal here is to make the execution boundary **explicit, enforceable, and measurable**.

---

## Website (Hackathon Requirement)

The repository includes a static website under `docs/` intended for judge inspection.  
It is a visual inspection layer over the same proofs (invariant, artifacts, evaluation, traces).  
It is not a backend service and does not change execution behavior.

---

## Status

Implemented and working:
- execution boundary enforcement
- runtime authority validation
- immutable execution artifacts
- decision-level evaluation summaries
- Opik tracing for enforcement proof

This repository is designed to be run and judged quickly.

---

## Author’s Note

This repository is a deliberate extraction from a larger internal system.

The goal is not to build more features.  
The goal is to make autonomy **legible**, **bounded**, and **provable**.
