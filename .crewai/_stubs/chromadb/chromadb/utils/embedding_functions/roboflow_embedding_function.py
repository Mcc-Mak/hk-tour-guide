"""Stub chromadb.utils.embedding_functions.roboflow_embedding_function module."""
from __future__ import annotations
from typing import Any


class _Dummy:
    def __class_getitem__(cls, item: Any) -> type:
        return cls


def __getattr__(name: str) -> Any:
    return type(name, (_Dummy,), {})
