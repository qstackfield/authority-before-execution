# Authority Before Execution  
### An Evaluation-First Control Plane for Autonomous Agents

---

## Overview

**Authority Before Execution** is a minimal, evaluation-first control plane for autonomous AI agents.

The system enforces a single invariant:

> **If explicit authority is not present at execution time, the next state does not exist.**

Agents are allowed to reason, plan, and propose actions - but they are **not allowed to commit state changes** unless authority is explicitly bound at the moment of execution.

This project demonstrates how separating **proposal** from **execution**, combined with continuous evaluation and observability, prevents responsibility drift in agentic systems and makes autonomy measurable instead of anecdotal.

---

## Why This Exists

Most agent safety and governance approaches operate **after** execution:
- logs are reviewed post-incident
- audits reconstruct intent after damage occurs
- responsibility is inferred rather than enforced

This project takes the opposite approach:

- **Authority is bound before execution**
- **Responsibility is explicit**
- **Outcomes are evaluated continuously**
- **Agent quality is measured over time**

This turns agent safety from storytelling into systems engineering.

---

## Core Principles

1. **Proposal ≠ Execution**  
   Agents may suggest actions, but execution is a separate, gated step.

2. **Authority Is Time-Bound**  
   Approval must exist *at execution time*. Past approval is not sufficient.

3. **No Authority → No State Change**  
   If approval is missing or expired, execution is blocked by design.

4. **Everything Is Observable**  
   Proposals, approvals, denials, executions, and outcomes are fully traced.

5. **Evaluation Comes First**  
   Agent behavior is continuously evaluated using structured metrics, not vibes.

---

## What This Project Demonstrates

This repository is a **focused vertical slice**, not a full platform.

It demonstrates:
- a single autonomous agent workflow
- explicit execution gating
- approval artifacts with scope and expiration
- auditable decision flow
- Opik-based tracing, experiments, and evaluations
- measurable improvement across agent runs

It intentionally avoids:
- large infrastructure
- multi-agent orchestration
- production authentication systems
- external integrations

Clarity beats scale for this demonstration.

---

## Architecture (High Level)

<pre>
User Task
   ↓
Agent (Reasoning + Proposal)
   ↓
Evaluation + Trace (Opik)
   ↓
Approval Gate
   ├─ Approved → Execute → Outcome Traced
   └─ Denied   → Block   → Denial Traced
</pre>

Execution is impossible without a valid approval artifact at the moment of commit.

---

## Evaluation & Observability

This project uses **Opik** to treat evaluation as a first-class system primitive.

Tracked signals include:
- decision correctness
- safety and policy alignment
- unnecessary retries
- execution denials
- trajectory efficiency
- outcome quality

Multiple runs of the same task can be compared to show **measurable improvement**, regressions, and tradeoffs.

---

## Hackathon Context

This project is submitted to the **Encode Club COMET Resolution v2 Hackathon**, with a primary focus on:

- **Best Use of Opik**

It is designed to showcase:
- evaluation-driven agent design
- observability beyond logs
- governance enforced at execution time

---

## Status

**Status:** Onboarding complete. Build begins with hackathon start.

Current focus:
- defining the execution boundary
- implementing approval gating
- instrumenting full traces and evaluations
- preparing a clear, reproducible demo

This repository will evolve incrementally with a working vertical slice and documented experiments.

---

## Running the Project (Coming Soon)

Instructions for running the demo locally will be added once the initial vertical slice is complete.

---

## Author’s Note

This repository represents a **deliberate extraction** from a larger internal system, scoped specifically to demonstrate authority-before-execution and evaluation-driven agent governance.

The goal is not to build more features.  
The goal is to make autonomy **legible, bounded, and provable**.
