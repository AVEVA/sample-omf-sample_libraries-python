from __future__ import annotations

from dataclasses import dataclass
from .Serializeable import Serializeable

from .OMFEnumValue import OMFEnumValue
from .OMFFormatCode import OMFFormatCode
from .OMFTypeCode import OMFTypeCode


@dataclass
class OMFEnum(Serializeable):
    Values: list[OMFEnumValue]
    Type: OMFTypeCode = None
    Format: OMFFormatCode = None
