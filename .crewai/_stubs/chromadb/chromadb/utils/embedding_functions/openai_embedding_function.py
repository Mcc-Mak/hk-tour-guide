"""Stub chromadb.utils.embedding_functions.openai_embedding_function module."""
from __future__ import annotations
from typing import Any


class _Dummy:
    def __class_getitem__(cls, item: Any) -> type:
        return cls


class EmbeddingFunction(_Dummy):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


class OpenAIEmbeddingFunction(EmbeddingFunction):
    pass


def __getattr__(name: str) -> Any:
    return type(name, (_Dummy,), {})
