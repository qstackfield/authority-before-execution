## Core Enforcement Logic

This directory contains the **execution-time enforcement boundary**.

- `executor.py` - the only location where state change is permitted
- `authority_gate.py` - fail-closed authority validation
- `artifact_exporter.py` - immutable execution evidence
- `evaluation.py` - aggregate outcome analysis

No code outside this directory can cause state change.
