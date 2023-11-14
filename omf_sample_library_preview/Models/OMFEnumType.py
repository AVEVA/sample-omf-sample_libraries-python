from __future__ import annotations

from dataclasses import dataclass

from .OMFEnum import OMFEnum
from .OMFEnumValue import OMFEnumValue
from .OMFType import OMFType
from .OMFTypeCode import OMFTypeCode
from .OMFFormatCode import OMFFormatCode


@dataclass
class OMFEnumType(OMFType):
    def __init__(self, Id: str, Values: list[OMFEnumValue], Type: OMFTypeCode = None, Format: OMFFormatCode = None):
        enum = OMFEnum(Values, Type, Format)
        super().__init__(Id, Enum=enum)
