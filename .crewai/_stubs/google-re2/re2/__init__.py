"""Stub re2 package for musllinux compatibility.

The real google-re2 package provides Python bindings to Google's RE2 C++
library, which has no musllinux wheels. It's a transitive dependency of
cel-python (via crewai), used only for Flow CEL expression evaluation. This
project does not use Flow expressions, so the stub is never called at runtime.
"""

from __future__ import annotations

from typing import Any


def compile(*args: Any, **kwargs: Any) -> Any:
    """Stub compile — raises if ever called (Flow CEL not used)."""
    raise NotImplementedError(
        "google-re2 stub: RE2 regex is not available in this deployment. "
        "Install the real google-re2 package on a supported platform."
    )
