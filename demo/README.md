## Demo entry points (judge guide)

Start here:

1. `python3 -m demo.run_demo`
   - Runs the canonical enforcement demo
   - Produces allow/deny artifacts
   - Emits Opik trace at execution.commit

Optional deep dives:

2. `run_prompt_injection.py`
   - Shows why prompt-only controls fail

3. `experiment_compare.py`
   - Compares agent-only vs execution-gated behavior

4. `run_authority_drift.py`
   - Shows time-bound authority expiration
