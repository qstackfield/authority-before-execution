# Authority Before Execution

## Evaluation-First Governance for Autonomous Agents

Authority Before Execution is a minimal control plane for autonomous agents where **execution is impossible without explicit, runtime authority**.

The system enforces a single invariant:

> **If authority is not present, valid, and in scope at execution time, the state transition does not occur.**

Agents are free to reason, plan, and propose actions.  
They are **not** allowed to commit changes unless authority is bound at the moment of execution.

This project demonstrates how separating **proposal**, **approval**, and **execution**, combined with continuous evaluation and observability, turns agent safety from policy rhetoric into an enforceable system property.

---

## Quick Proof (Read This First)

This repository contains real enforcement, not simulated behavior.

Run this:

    python3 -m demo.run_demo

What you will observe:

1. Execution without authority is blocked (fail-closed)
2. Execution with valid, scoped authority is permitted
3. Authority out of scope is rejected
4. Expired authority is rejected
5. Each attempt produces an immutable JSON artifact under `docs/artifacts/`

Artifacts are written to:

    docs/artifacts/

Each artifact contains:
- decision identifier
- execution timestamp
- authority context
- allow/deny outcome
- denial reason (if applicable)

No UI. No mocks. No post-hoc interpretation.

---

## Why This Exists

Most agent governance approaches operate *after* execution:
- logs are reviewed post-incident
- intent is reconstructed after damage occurs
- responsibility is inferred, not enforced

This project takes the opposite stance:
- **authority is enforced before execution**
- **responsibility is explicit, scoped, and time-bound**
- **execution outcomes are measurable**
- **governance quality is observable over time**

This is not about preventing agents from acting.  
It is about making **who allowed what, when, and why** a first-class signal.

---

## Core Principles

1. **Proposal is not execution**  
   Agents may propose freely. Execution is a separate, gated boundary.

2. **Authority is runtime-bound**  
   Approval must exist at execution time. Prior approval alone is insufficient.

3. **Fail closed by design**  
   Missing, expired, or out-of-scope authority blocks execution deterministically.

4. **Governance is observable**  
   Every allow, deny, scope violation, and expiration is traced and recorded.

5. **Evaluation comes first**  
   Agent behavior is measured with data, not narratives.

---

## What This Project Demonstrates

This repository is a deliberate vertical slice, not a platform.

It demonstrates:
- a typed decision contract (proposal → authority → execution)
- a single explicit execution boundary
- scoped and time-bound approvals
- deterministic allow/deny behavior
- Opik-based tracing and decision-level evaluation
- governance quality metrics (not just success rates)

It intentionally avoids:
- infrastructure sprawl
- UI layers
- orchestration frameworks
- production authentication systems
- feature completeness

Clarity beats scale for this demonstration.

---

## Architecture (High Level)

User Task  
↓  
Agent (Reasoning + Proposal)  
↓  
Evaluation + Trace (Opik)  
↓  
Authority Gate (Runtime Enforcement)  
- Approved → Execute → Outcome Traced  
- Denied → Block → Denial Traced  

**No valid authority → no state change.**

---

## How to Read the Demo

This demo is not a chatbot or UI.  
It is a deterministic execution boundary evaluated through artifacts.

To understand it:

1. Run:

       python3 -m demo.run_demo

2. Observe the console output for each execution attempt.
3. Inspect `docs/artifacts/*.json` to verify outcomes.
4. Review the evaluation summary printed at the end.

Each execution attempt differs only by the authority binding.  
The proposal remains constant.

---

## Evaluation and Observability

Opik is used as an evaluation substrate, not a logging sink.

Tracked signals include:
- execution allow/deny rates
- denial reasons (missing, expired, out-of-scope authority)
- authority scope correctness
- overbroad approval usage
- comparative outcomes across runs

This lets teams distinguish **execution success** from **governance quality**.

An execution can succeed and still be governance-poor.  
That distinction is the point.

---

## Hackathon Context

Submitted to **Encode - Commit To Change: An AI Agents Hackathon**.

Primary focus:
- **Best Use of Opik**

This project demonstrates:
- evaluation-driven agent design
- observability beyond logs
- authority enforced at execution time
- measurable governance signals surfaced via Opik

---

## Status

Core invariants are implemented and enforced:
- execution boundary is explicit
- authority is runtime-validated
- enforcement artifacts are immutable JSON
- decision-level evaluation is operational

This repository is demo-ready.

---

## Author’s Note

This repository is a deliberate extraction from a larger internal system.

The goal is not to add features.  
The goal is to make autonomy **legible**, **bounded**, and **provable**.
