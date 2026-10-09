"""Stub onnxruntime package for musllinux compatibility.

The real onnxruntime has no musllinux wheels. It's a transitive dependency of
chromadb (via crewai), used only for local RAG embeddings. This project does
not use RAG, so the stub is never called at runtime.
"""

from __future__ import annotations

from typing import Any


class InferenceSession:
    """Stub InferenceSession — raises if ever called (RAG not used)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError(
            "onnxruntime stub: RAG embeddings are not available in this "
            "deployment. Install the real onnxruntime on a supported platform."
        )
