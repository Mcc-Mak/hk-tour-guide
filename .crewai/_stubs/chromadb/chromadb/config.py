"""Stub chromadb.config module — pydantic-compatible."""
from __future__ import annotations
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class Settings:
    """Stub Settings that accepts any kwargs and is pydantic-compatible."""

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.any_schema()


def __getattr__(name: str) -> Any:
    return type(name, (), {})
