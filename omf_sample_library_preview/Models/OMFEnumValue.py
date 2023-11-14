from __future__ import annotations

from dataclasses import dataclass

from .Serializeable import Serializeable


@dataclass
class OMFEnumValue(Serializeable):
    Name: str
    Value: int
