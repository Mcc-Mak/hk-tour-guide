"""Stub chromadb.api.configuration module — pydantic-compatible."""
from __future__ import annotations
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class _Dummy:
    def __class_getitem__(cls, item: Any) -> type:
        return cls

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.any_schema()


class CollectionConfigurationInterface(_Dummy):
    pass


def __getattr__(name: str) -> Any:
    return type(name, (_Dummy,), {})
