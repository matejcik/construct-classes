import typing as t

import construct as c

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
