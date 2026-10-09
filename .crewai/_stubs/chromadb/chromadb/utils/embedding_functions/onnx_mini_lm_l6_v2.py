"""Stub chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 module."""
from __future__ import annotations
from typing import Any


class _Dummy:
    def __class_getitem__(cls, item: Any) -> type:
        return cls


class ONNXMiniLM_L6_V2(_Dummy):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


def __getattr__(name: str) -> Any:
    return type(name, (_Dummy,), {})
