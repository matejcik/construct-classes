import typing as t
from dataclasses import FrozenInstanceError

import construct as c
import pytest

from construct_classes import Struct, subcon


class BasicStruct(Struct):
    a: int
    b: int

    SUBCON = c.Struct(
        "a" / c.Int8ub,
        "b" / c.Int8ub,
    )


def test_basic():
    bs = BasicStruct(a=5, b=10)

    compiled = bs.build()
    parsed = BasicStruct.parse(compiled)
    assert parsed == bs


class SubconStruct(Struct):
    a: int
    b: BasicStruct = subcon(BasicStruct)

    SUBCON = c.Struct(
        "a" / c.Int8ub,
        "b" / BasicStruct.SUBCON,
    )


def test_subcon():
    ss = SubconStruct(a=5, b=BasicStruct(a=10, b=20))

    compiled = ss.build()
    parsed = SubconStruct.parse(compiled)
    assert parsed == ss

    substr = parsed.b.build()
    assert substr in compiled


class WithDefaultFactory(Struct):
    array: t.List[BasicStruct] = subcon(BasicStruct, default_factory=list)

    SUBCON = c.Struct(
        "array" / c.Array(2, BasicStruct.SUBCON),
    )


def test_default():
    dd = WithDefaultFactory()
    assert dd.array == []


class MoreFieldsInConstruct(Struct):
    a: int

    SUBCON = c.Struct(
        "a" / c.Int8ub,
        "b" / c.Tell,
    )


def test_more_fields():
    MoreFieldsInConstruct.parse(b"\x01")


class DefaultsNotLast(Struct):
    a: int = 1
    b: int

    SUBCON = c.Struct(
        "a" / c.Int8ub,
        "b" / c.Int8ub,
    )


def test_defaults_not_last():
    rebuilt = DefaultsNotLast(b=5).build()
    reparsed = DefaultsNotLast.parse(rebuilt)
    assert reparsed.a == 1
    assert reparsed.b == 5


class DataclassPassthrough(Struct, frozen=True, eq=False):
    a: int

    SUBCON = c.Struct(
        "a" / c.Int8ub,
    )


def test_dataclass_passthrough():
    a = DataclassPassthrough(a=1)
    with pytest.raises(FrozenInstanceError):
        a.a = 2  # type: ignore  # yes, it is an error
    assert a.a == 1

    # eq is not implemented
    b = DataclassPassthrough(a=1)
    assert a != b


def test_indirect_descendant():
    """
    regression test for #5: a subclass of a subclass of a Struct would have caused an
    exception on definition
    """

    class Sub(BasicStruct):
        pass
