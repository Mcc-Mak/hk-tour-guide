"""Stub chromadb.api.types module — subscriptable + pydantic-compatible."""
from __future__ import annotations
from typing import Any, Generic, TypeVar

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

Documents = list[str]
Embeddings = list[list[float]]

_T = TypeVar("_T")


class EmbeddingFunction(Generic[_T]):
    """Generic EmbeddingFunction stub — supports subscription and pydantic."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.any_schema()


class _Dummy:
    """Dummy type that supports subscription and pydantic."""

    def __class_getitem__(cls, item: Any) -> type:
        return cls

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.any_schema()


def __getattr__(name: str) -> Any:
    return type(name, (_Dummy,), {})
