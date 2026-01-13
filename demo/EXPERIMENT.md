## Experiment: Authority-Gated Execution

### Question
Does enforcing authority at execution time measurably change agent behavior?

### What Is Being Evaluated
The same proposed action is executed multiple times.
Only the **authority binding** changes.

The proposal itself does not.

See:
- `sample_decision.json` (canonical decision input)
- `sample_execution_result.json` (example execution outcome)

### Method
We ran identical decisions under two conditions:

1. No authority bound  
2. Explicit, scoped, time-bound authority bound at execution

Each decision was attempted multiple times and traced via Opik
at the execution boundary.

### Metrics
- Execution allow rate
- Denial reason distribution
- Authority misuse detection

### Result
Ungoverned executions were blocked 100% of the time.

Governed executions succeeded **only** when authority was:
- present
- scoped to the action
- unexpired at execution time

Expired or out-of-scope authority was denied.

### Why This Matters
This demonstrates that authority-before-execution is:
- enforceable (not advisory)
- observable (fully traced)
- measurable (decision-level metrics)

This is governance at the execution boundary,
not post-hoc review.

### Artifact Provenance

The JSON files in this directory are snapshots of real execution results
produced by this demo.

They are included to make execution behavior inspectable without requiring
judges to run the code.

- `sample_decision.json` shows the canonical decision input.
- `sample_execution_result.json` shows the structured result returned by
  `executor.execute()` for an authority-approved execution.

These artifacts reflect actual runtime behavior and are not hard-coded
inputs to the system.
