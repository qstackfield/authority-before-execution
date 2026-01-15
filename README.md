# Authority Before Execution
## Execution-Time Governance for Autonomous Agents  
**Encode · Commit to Change Hackathon Submission**

---

## TL;DR

**Authority Before Execution makes unsafe AI actions impossible by enforcing explicit, scoped authority at the moment of execution and proves it with measurable evidence.**

This is not a guardrail.  
This is an execution boundary.

**Judges: start here**

Run the baseline demo to verify enforcement immediately:

    python3 -m demo.run_demo

## Required: Inspection website

This submission includes a required website:

https://qstackfield.github.io/authority-before-execution/

The website is a **read-only inspection surface** over execution artifacts.
It does not perform enforcement or simulation.

All authority checks, enforcement, and artifact generation occur at execution time
in `core/executor.py`.

---

## The problem

AI agents are becoming autonomous enough to:
- deploy code
- modify infrastructure
- delete data
- trigger irreversible actions

Most safety approaches focus on:
- prompt hardening
- alignment tuning
- intent classification
- post-incident logging

All of these approaches share the same flaw:

**They operate after execution.**

But harm does not occur during reasoning.  
Harm occurs during **state change**.

This project governs execution - not thought.

---

## The core invariant

**Invariant ID:** `ABE-EXEC-001`

> If explicit authority is not present, valid, and in scope at execution time,  
> the state transition must not occur.

Everything in this repository exists to enforce, test, and prove this rule.

---

## What this system does

Authority Before Execution separates autonomy into three explicit phases:

1. **Proposal**  
   Agents may reason freely and propose any action.

2. **Authority**  
   Approval is explicit, scoped, and time-bound.

3. **Execution**  
   The action is permitted **only if authority is valid at execution time**.

If authority is:
- missing
- expired
- reused
- out of scope

Execution is deterministically blocked.

No retries.  
No reinterpretation.  
No “best effort.”

---

## Why this is different

Most systems ask:

> “Did the agent behave correctly?”

This system asks:

> **“Should this execution have been allowed to happen at all?”**

Prompt injection does not matter here.  
Alignment failures do not matter here.  
Intent does not matter here.

Only execution-time authority determines reality.

---

## What is proven (not claimed)

This repository demonstrates **real enforcement**, not simulated safety.

It proves:
- execution without authority is impossible (fail-closed)
- scope violations are deterministically blocked
- expired approvals cannot be reused (replay / drift prevention)
- prompt injection cannot escalate authority
- overbroad approvals are detectable and measurable
- governance quality is observable independently of execution success

Every claim is backed by:
- deterministic runs
- immutable artifacts
- repeatable evaluation
- measurable deltas

---

## Demo suite

All demos enforce the same invariant and execution boundary.

### Demo 0 - Baseline execution proof

Run:

    python3 -m demo.run_demo

Proves:
- missing authority → BLOCKED
- valid scoped authority → PERMITTED
- wrong scope → BLOCKED
- expired authority → BLOCKED

Each attempt writes an immutable JSON artifact under `docs/artifacts/`.

---

### Demo A - Controlled variance at scale

Run:

    python3 -m demo.run_variance --n 50 --seed 7
    python3 -m demo.run_variance --n 200 --seed 7 --quiet

Proves:
- the invariant holds across dozens or hundreds of executions
- outcomes are deterministic and reproducible
- deny reasons form a measurable distribution
- overbroad authority can succeed and is flagged as governance-poor

This is not fuzzing.  
It is controlled, explainable variance.

---

### Demo B - Prompt injection is irrelevant

Run:

    python3 -m demo.run_prompt_injection

Proves:
- prompt injection cannot escalate authority
- reasoning content does not affect execution
- only execution-time authority determines state change

Alignment without authority is theater.

---

### Demo C - Authority drift and replay prevention

Run:

    python3 -m demo.run_authority_drift

Proves:
- authority cannot be reused after expiration
- replay attempts fail deterministically
- execution-time validation prevents drift

---

### Demo D - Comparative agent evaluation

Run:

    python3 -m demo.run_comparative_agent --n 12
    python3 -m demo.run_comparative_agent --n 12 --scope none

Proves:
- same agent, same prompts, different outcomes
- governance changes behavior
- overbroad approvals allow execution but degrade governance quality

**Key insight:**  
An execution can succeed and still be unsafe.

---

## Evaluation and observability (Opik)

Opik is used as an **evaluation substrate**, not a logging sink.

Tracked signals include:
- allow vs deny rates
- deny reason distributions
- scope violations
- expired authority usage
- overbroad authority usage
- governed vs ungoverned deltas

Execution success ≠ safe execution.  
This system makes that distinction visible.

---

## Execution artifacts

Every execution attempt produces an immutable JSON artifact:

    docs/artifacts/

Each artifact includes:
- decision ID
- timestamp
- proposal details
- authority context
- allow / deny outcome
- denial reason (if applicable)

If an artifact exists, execution occurred.

---

## Architecture (minimal by design)

Agent (reasoning + proposal)  
↓  
Evaluation & tracing (Opik)  
↓  
Authority gate (execution boundary)  
- permitted → execute → artifact  
- blocked → no state change → artifact  

No valid authority means no state change.

---

## The console

The backend already produces the truth.

The console exposes:
- every execution attempt
- bound authority and scope
- TTL at execution time
- allow / deny outcomes
- governance quality metrics

The console does not interpret behavior.  
It reveals reality.

---

## Hackathon context

Submitted to **Encode · Commit to Change -  AI Agents Hackathon**.

Primary focus:
- **Best Use of Opik**

This project uses Opik to:
- enforce invariants
- evaluate execution outcomes
- compare governed vs ungoverned behavior
- surface governance failures
- measure execution safety

---

## Status

The backend is complete and frozen:
- invariant enforced
- demos deterministic
- artifacts immutable
- evaluation operational
- scale validated

All future work (console, site, demo video) reflects this reality.

---

## Author’s note

This repository is a deliberate extraction from a larger internal system.

The goal is not to add features.

The goal is to make autonomy:
- legible
- bounded
- provable

Execution is where responsibility lives.  
This system enforces that truth.
