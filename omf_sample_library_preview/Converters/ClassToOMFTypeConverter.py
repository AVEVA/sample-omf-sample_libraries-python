from datetime import datetime
from types import UnionType, NoneType
from typing import Any, get_type_hints, get_origin, get_args

from ..Models import OMFClassification, OMFExtrapolationMode, OMFFormatCode, OMFInterpolationMode, OMFType, OMFTypeCode, OMFTypeProperty


def getOMFTypeFromPythonType(type_hint: type) -> (OMFTypeCode | list[OMFTypeCode], OMFFormatCode, OMFTypeProperty, OMFTypeProperty):
    omf_type_code = OMFTypeCode.String
    omf_format_code = None
    items = None
    additional_properties = None

    if type_hint is NoneType:
        raise ValueError('Invalid OMF Type: NoneType is not allowed')

    if isinstance(type_hint, UnionType):
        args = get_args(type_hint)
        if len(args) > 2:
            raise ValueError(
                'Invalid OMF Type: Too many types associated with property')
        if args[0] is NoneType and args[1] is NoneType:
            raise ValueError(
                'Invalid OMF Type: Both types for a Union Type cannot be None')
        if args[0] is not NoneType and args[1] is not NoneType:
            raise ValueError(
                'Invalid OMF Type: At least one type for a Union Type must be None')
        if args[0] is not NoneType:
            nullable_type = args[0]
        else:
            nullable_type = args[1]
        temp_omf_type_code, omf_format_code, items, additional_properties = getOMFTypeFromPythonType(
            nullable_type)
        omf_type_code = [temp_omf_type_code, OMFTypeCode.Null]
    elif type_hint is int:
        omf_type_code = OMFTypeCode.Integer
    elif type_hint is float:
        omf_type_code = OMFTypeCode.Number
    elif type_hint is datetime:
        omf_format_code = OMFFormatCode.DateTime
    elif type_hint is bool:
        omf_type_code = OMFTypeCode.Boolean
    elif get_origin(type_hint) is list:
        arg = get_args(type_hint)[0]
        result = getOMFTypeFromPythonType(arg)
        if result[0] == OMFTypeCode.Array or result[0] == OMFTypeCode.Object:
            raise ValueError(
                'Invalid OMF Type: Nested lists and objects are not supported')
        items = OMFTypeProperty(result[0], result[1])
        omf_type_code = OMFTypeCode.Array
    elif get_origin(type_hint) is dict:
        args = get_args(type_hint)
        if args[0] is not str:
            raise ValueError(
                'Invalid OMF Type: Dictionaries must have key of type string')
        result = getOMFTypeFromPythonType(args[1])
        if result[0] == OMFTypeCode.Array or result[0] == OMFTypeCode.Object:
            raise ValueError(
                'Invalid OMF Type: Nested lists and objects are not supported')
        additional_properties = OMFTypeProperty(result[0], result[1])
        omf_type_code = OMFTypeCode.Object
        omf_format_code = OMFFormatCode.Dictionary

    return (omf_type_code, omf_format_code, items, additional_properties)


def getOMFTypePropertyPythonProperty(prop: property) -> OMFTypeProperty:
    type_hint = get_type_hints(prop.fget).get('return', None)
    omf_type_code, omf_format_code, items, additional_properties = getOMFTypeFromPythonType(
        type_hint)

    if hasattr(prop.fget, '__omf_type_property'):
        type_property = getattr(prop.fget, '__omf_type_property')
        if not type_property.Format:
            type_property.Format = omf_format_code
        if not type_property.Type:
            type_property.Type = omf_type_code
        return type_property
    return OMFTypeProperty(omf_type_code, omf_format_code, items, AdditionalProperties=additional_properties)


def convert(omf_class: type) -> OMFType:
    if hasattr(omf_class, '__omf_type'):
        omf_type = getattr(omf_class, '__omf_type')
    else:
        omf_type = OMFType(omf_class.__name__, OMFClassification.Dynamic)

    properties = [
        (k, getOMFTypePropertyPythonProperty(v))
        for k, v in omf_class.__dict__.items()
        if isinstance(v, property)]
    omf_properties = {}
    for id, prop in properties:
        omf_properties.update({id: prop})
    omf_type.Properties = omf_properties
    return omf_type


def omf_type(Id=None,
             Classification: OMFClassification = OMFClassification.Dynamic,
             Type: str = 'Object',
             Version: str = None,
             Name: str = None,
             Description: str = None,
             Tags: list[str] = None,
             Metadata: dict[str, Any] = None,
             Enum: dict[str, Any] = None,
             Extrapolation: OMFExtrapolationMode = None):

    def wrap(cls):
        id = Id
        if not id:
            id = cls.__name__
        omf_type_attribute = OMFType(
            id, Classification, Type, Version, Name, Description, Tags, Metadata, Enum, Extrapolation)
        setattr(cls, '__omf_type', omf_type_attribute)

        return cls

    return wrap


def omf_type_property(Type: OMFTypeCode | list[OMFTypeCode] = None,
                      Format: OMFFormatCode = None,
                      Items: 'OMFTypeProperty' = None,
                      RefTypeId: str = None,
                      IsIndex: bool = None,
                      IsQuality: bool = None,
                      Name: str = None,
                      Description: str = None,
                      Uom: str = None,
                      Minimum: float | int = None,
                      Maximum: float | int = None,
                      Interpolation: OMFInterpolationMode = None):

    def wrap(func):
        omf_type_property_attribute = OMFTypeProperty(
            Type, Format, Items, RefTypeId, IsIndex, IsQuality,  Name, Description, Uom, Minimum, Maximum, Interpolation)
        setattr(func, '__omf_type_property', omf_type_property_attribute)
        return func

    return wrap
