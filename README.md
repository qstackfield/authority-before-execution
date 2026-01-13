# Authority Before Execution  
### Evaluation-First Governance for Autonomous Agents

---

## Overview

**Authority Before Execution** is a minimal control plane for autonomous agents where **execution is impossible without explicit, runtime authority**.

The system enforces a single invariant:

> **If authority is not present, valid, and in scope at execution time, the state transition does not occur.**

Agents are free to reason, plan, and propose actions.  
They are **not** allowed to commit changes unless authority is bound at the moment of execution.

This project demonstrates how separating **proposal**, **approval**, and **execution**, combined with continuous evaluation and observability, turns agent safety from policy rhetoric into an enforceable system property.

---

## Why This Exists

Most agent governance approaches operate *after* execution:
- logs are reviewed post-incident  
- intent is reconstructed after damage occurs  
- responsibility is inferred, not enforced  

This project takes the opposite stance:

- **Authority is enforced before execution**
- **Responsibility is explicit, scoped, and time-bound**
- **Execution outcomes are measurable**
- **Governance quality is observable over time**

This is not about preventing agents from acting.  
It is about making *who allowed what, when, and why* a first-class signal.

---

## Core Principles

1. **Proposal ≠ Execution**  
   Agents may propose freely. Execution is a separate, gated boundary.

2. **Authority Is Runtime-Bound**  
   Approval must exist *at execution time*. Prior approval alone is insufficient.

3. **Fail Closed by Design**  
   Missing, expired, or out-of-scope authority blocks execution deterministically.

4. **Governance Is Observable**  
   Every allow, deny, scope violation, and expiration is traced.

5. **Evaluation Comes First**  
   Agent behavior is measured with data, not narratives.

---

## What This Project Demonstrates

This repository is a **deliberate vertical slice**, not a platform.

It demonstrates:
- a typed decision contract (proposal → authority → execution)
- explicit execution gating
- scoped and time-bound approvals
- deterministic allow / deny behavior
- Opik-based tracing and experiment comparison
- **governance quality metrics**, not just success rates

It intentionally avoids:
- infrastructure sprawl
- UI layers
- orchestration frameworks
- production auth systems
- feature completeness

Clarity beats scale for this demonstration.

---

## Non-Goals

This project intentionally does **not** attempt to solve:

- identity or role-based access control
- approval workflow UIs
- policy DSLs or rule engines
- credential storage or key management
- multi-agent orchestration
- model training or fine-tuning
- production deployment concerns

Those problems matter - but they are **orthogonal**.

The goal here is to make the **execution boundary explicit, enforceable, and measurable**.

---

## Architecture (High Level)

**User Task**  
↓ 
**Agent (Reasoning + Proposal)**  
↓  
**Evaluation + Trace (Opik)**  
↓  
**Authority Gate**  
- Approved → Execute → Outcome Traced  
- Denied → Block → Denial Traced  

No valid authority → no state change.

---

## How to Read the Demo

This repository is intentionally minimal.

The demo is not a UI or chatbot.
It is a deterministic execution boundary evaluated through artifacts.

To understand the demo:

1. Review `demo/sample_artifact.json`  
   This represents the canonical decision under evaluation.

2. Run `demo/run_demo.py`  
   Each execution attempt keeps the proposal constant and
   varies only the authority binding.

3. Observe execution outcomes  
   Execution is allowed or denied solely based on authority
   validity, scope, and expiration at runtime.

4. Review evaluation summaries  
   Aggregated metrics show how often authority is present,
   violated, or expired for a given decision.

All execution outcomes are traced and evaluated using Opik.

---
	
## Evaluation & Observability

Opik is used as an **evaluation substrate**, not a logging sink.

Tracked signals include:
- execution allow / deny rates
- denial reasons (missing, expired, out-of-scope authority)
- authority scope correctness
- overbroad approval usage
- comparative outcomes across runs

This allows teams to distinguish:
- *execution success*  
- from *governance quality*

An execution can succeed **and still be flagged as governance-poor**.

That distinction is the point.

---

## Hackathon Context

Submitted to **Encode - Commit To Change: An AI Agents Hackathon**  
Primary focus:

- **Best Use of Opik**

This project showcases:
- evaluation-driven agent design
- observability beyond logs
- authority enforced at execution time
- measurable governance signals Opik can surface

---

## Status

**Status:** Core invariants implemented.  
Decision-level evaluation and comparative experiments in place.

Current focus:
- refining authority quality metrics
- expanding comparative experiment coverage
- preparing a clear, reproducible demo

---

## Running the Project

Local run instructions will be added once the demo scenario set is finalized.

---

## Author’s Note

This repository is a **deliberate extraction** from a larger internal system, scoped specifically to demonstrate authority-before-execution and evaluation-driven governance.

The goal is not to build more features.  
The goal is to make autonomy **legible, bounded, and provable**.
