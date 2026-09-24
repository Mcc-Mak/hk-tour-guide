"""Stub lancedb package for musllinux compatibility.

The real lancedb package has no musllinux wheels. This stub satisfies the
install-time dependency for crewai, which only uses lancedb for its Memory
storage feature (lazily imported). This project does not use Memory, so the
stub is never called at runtime.
"""

from __future__ import annotations

from typing import Any


def connect(*args: Any, **kwargs: Any) -> Any:
    """Stub connect — raises if ever called (Memory storage is not used)."""
    raise NotImplementedError(
        "lancedb stub: Memory storage is not available in this deployment. "
        "Install the real lancedb package on a supported platform to enable it."
    )
