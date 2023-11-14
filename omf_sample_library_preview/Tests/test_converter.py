from datetime import datetime
import pytest
from types import NoneType

from ..Converters.ClassToOMFTypeConverter import getOMFTypeFromPythonType, omf_type, omf_type_property, convert
from ..Models import OMFClassification, OMFFormatCode, OMFType, OMFTypeCode, OMFTypeProperty


@pytest.mark.parametrize(
    "type_hint,expected",
    [
        (bool, (OMFTypeCode.Boolean, None, None, None)),
        (int, (OMFTypeCode.Integer, None, None, None)),
        (float, (OMFTypeCode.Number, None, None, None)),
        (datetime, (OMFTypeCode.String, OMFFormatCode.DateTime, None, None)),
        (float | None, ([OMFTypeCode.Number,
         OMFTypeCode.Null], None, None, None)),
        (None | float, ([OMFTypeCode.Number,
         OMFTypeCode.Null], None, None, None)),
        (list[int], (OMFTypeCode.Array, None,
         OMFTypeProperty(OMFTypeCode.Integer), None)),
        (dict[str, str], (OMFTypeCode.Object, OMFFormatCode.Dictionary,
         None, OMFTypeProperty(OMFTypeCode.String)))
    ]
)
def test_validGetOMFTypeFromPythonType(type_hint: type, expected: (OMFTypeCode, OMFFormatCode, OMFTypeProperty, OMFTypeProperty)):
    assert getOMFTypeFromPythonType(type_hint) == expected


@pytest.mark.parametrize(
    "type_hint",
    [
        NoneType,
        float | int,
        float | int | str,
        dict[int, str],
        list[list[int]],
        dict[str, dict[str, str]]
    ]
)
def test_invalidGetOMFTypeFromPythonType(type_hint: type):
    with pytest.raises(ValueError):
        getOMFTypeFromPythonType(type_hint)


@omf_type()
class MyClass1:
    def __init__(self, timestamp: datetime, value: float):
        self.__timestamp = timestamp
        self.__value = value

    @property
    @omf_type_property(IsIndex=True)
    def timestamp(self) -> datetime:
        return self.__timestamp

    @property
    def value(self) -> float:
        return self.__value


@pytest.mark.parametrize(
    "omf_class,expected",
    [
        (MyClass1, OMFType('MyClass1', OMFClassification.Dynamic, Properties={
            'timestamp': OMFTypeProperty(OMFTypeCode.String, OMFFormatCode.DateTime, IsIndex=True),
            'value': OMFTypeProperty(OMFTypeCode.Number)
        }))
    ]
)
def test_convert(omf_class: type, expected: OMFType):
    assert convert(omf_class) == expected
