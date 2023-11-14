from __future__ import annotations

from .OMFLinkValue import OMFLinkValue
from .OMFData import OMFData


class OMFLinkData(OMFData):
    def __init__(self, Values: list[OMFLinkValue]):
        super().__init__[OMFLinkValue](Values, '__Link', None, None)
