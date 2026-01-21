from __future__ import annotations

import os
from typing import Callable


def observability_enabled() -> bool:
    """
    Observability is STRICTLY opt-in.

    Enabled only when:
        ABE_ENABLE_OBSERVABILITY=1

    Default behavior:
        - no imports
        - no logging
        - no network calls
    """
    return os.getenv("ABE_ENABLE_OBSERVABILITY", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def trace_if_enabled(name: str):
    """
    Conditional tracing decorator.

    Guarantees:
    - No side effects unless explicitly enabled
    - No exceptions propagate
    - No impact on execution behavior
    """

    def decorator(fn: Callable):
        def wrapped(*args, **kwargs):
            if not observability_enabled():
                return fn(*args, **kwargs)

            try:
                from opik import track  # type: ignore
            except Exception:
                return fn(*args, **kwargs)

            try:
                traced = track(
                    name=name,
                    capture_input=True,
                    capture_output=True,
                )(fn)
                return traced(*args, **kwargs)
            except Exception:
                return fn(*args, **kwargs)

        return wrapped

    return decorator
