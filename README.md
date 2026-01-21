# Authority Before Execution

**Execution-time governance for autonomous agents.**

This repository enforces a single invariant at the only place that matters:
**execution time**.

This is not intent filtering. 
This is not prompt hygiene.
This is an **execution boundary**.

---

## Invariant (ABE-EXEC-001)

If explicit authority is not present, valid, and in scope at execution time, 
the state transition must not occur.

This system exists to **enforce** that invariant and **prove it with evidence**.

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
