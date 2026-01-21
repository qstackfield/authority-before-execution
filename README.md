# Authority Before Execution

**Execution-time governance for autonomous agents.**

This repository demonstrates a single, enforceable invariant at the only place that matters: **execution time**.

It is not intent filtering. 
It is not prompt hygiene.
It is an **execution boundary**.

---

## Release Status

**v0.1.0 - Hackathon Evaluation Release**

- Stable checkpoint for judging and inspection
- Execution behavior is frozen (non-breaking changes only)
- Demo video will show the execution boundary in action

This version exists to be **run, inspected, and verified**.

---

## Invariant (ABE-EXEC-001)

If explicit authority is not present, valid, and in scope at execution time,
**the state transition must not occur**.

The system enforces this invariant and proves it with **runtime artifacts and boundary traces**, not post-hoc interpretation.

---

## Productivity Impact (ABE-PROD-001)

Authority Before Execution does not just improve safety. It removes work.

The system enforces execution-time authority, preventing invalid actions from
ever entering human workflows.

A runnable productivity proof demonstrates this effect:

    python3 -m demo.run_productivity_proof

### Example outcome (default run)

- 100 attempted actions
- 73 blocked at execution time
- 73% of potential human decisions eliminated

Each blocked action represents:

- a ticket that was never created
- a review that never happened
- a meeting that never needed to be scheduled

No queues.
No escalations.
No operational drag.

This is productivity enforced at execution time.

---

## Judges: Run it in 60 seconds

### Option A (Recommended): GitHub Codespaces (no local setup)

1. Open this repository on GitHub 
2. Click **Code → Codespaces → Create codespace on main**
3. In the Codespaces terminal, run:

    python3 -m demo.run_demo --compact

That’s it.

No API keys.
No configuration.
No setup.

The output you see **is the enforcement proof**.

Observability is optional and fully disabled by default; execution enforcement never depends on external services.

### What you should see

The demo performs **four execution attempts**:

- Missing authority → **BLOCKED**
- Valid scoped authority → **PERMITTED**
- Scope violation → **BLOCKED**
- Expired authority → **BLOCKED**

Final verdict:

**Invariant ABE-EXEC-001: HELD**

All invalid execution attempts were blocked at the execution boundary.

### Option B: Local execution

**Requirements:** Python 3.10+

Install dependencies:

    pip install -r requirements.txt

Run the demo:

    python3 -m demo.run_demo --compact

## Optional: Execution Tracing with Opik (Power Users)

This project integrates with **Opik** for optional execution tracing and evaluation.

**Opik is NOT required** to run the demo.

If Opik is already configured in your environment, the demo will automatically:

- Emit execution traces
- Record allow / deny outcomes
- Capture deny reasons
- Log the enforcement point: `execution.commit`

If Opik is not configured, the demo runs normally with **no errors or prompts**.

Observability (Opik) is bound to the execution boundary itself.
It’s opt-in and disabled by default, but when enabled it emits a trace at the exact commit point (execution.commit).
Enforcement never depends on logs, traces or dashboards.

## Inspection Site (Read-Only)

https://qstackfield.github.io/authority-before-execution/

This site is a **read-only inspection surface** for execution artifacts.

It does not:
- Enforce authority
- Simulate execution
- Run agents

All enforcement happens **only** at execution time inside:

- `core/executor.py`

## What this proves

Most AI safety mechanisms operate before execution:
- prompt filters
- intent classification
- policy text

This project proves a stronger guarantee:

**Unsafe actions cannot occur without explicit authority at execution time.**

If authority is:
- missing
- expired
- out of scope

The state transition is **blocked**, deterministically, every time.

## Repository layout (minimal by design)

- `core/`
  Execution boundary, authority gate, and artifact export

- `demo/`
  Deterministic demos proving enforcement behavior

- `docs/`
  GitHub Pages inspection site and execution artifacts

---

**Judges first. Enforcement proven. Evidence included.**
