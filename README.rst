=================
construct-classes
=================

.. image:: https://img.shields.io/pypi/v/construct-classes.svg
        :target: https://pypi.python.org/pypi/construct-classes

.. .. image:: https://readthedocs.org/projects/construct-classes/badge/?version=latest
..         :target: https://construct-classes.readthedocs.io/en/latest/?badge=latest
..         :alt: Documentation Status

.. image:: https://pyup.io/repos/github/trezor/construct-classes/shield.svg
     :target: https://pyup.io/repos/github/trezor/construct-classes/
     :alt: Updates


Parse your binary data into dataclasses. Pack your dataclasses into binary data.

:code:`construct-classes` rely on `construct`_ for parsing and packing. The
programmer needs to manually write the Construct expressions. There is also no type
verification, so it is the programmer's responsibility that the dataclass and the
Construct expression match.

For fully type annotated experience, install `construct-typing`_.

This package typechecks with `mypy`_ and `pyright`_.

.. _construct: https://construct.readthedocs.io/en/latest/
.. _construct-typing: https://github.com/timrid/construct-typing
.. _mypy: https://mypy.readthedocs.io/en/stable/
.. _pyright: https://github.com/microsoft/pyright

Usage
-----

Any child of :code:`Struct` is a Python dataclass. It expects a Construct :code:`Struct`
expression in the :code:`SUBCON` attribute. The names of the attributes of the dataclass
must match the names of the fields in the Construct struct.

.. code-block:: python

    import construct as c
    from construct_classes import Struct, subcon

    class BasicStruct(Struct):
        x: int
        y: int
        description: str

        SUBCON = c.Struct(
            "x" / c.Int32ul,
            "y" / c.Int32ul,
            "description" / c.PascalString(c.Int8ul, "utf8"),
        )


    data = b"\x01\x00\x00\x00\x02\x00\x00\x00\x05hello"
    parsed = BasicStruct.parse(data)
    print(parsed)  # BasicStruct(x=1, y=2, description='hello')

    new_data = BasicStruct(x=100, y=200, description="world")
    print(new_data.build())  # b'\x64\x00\x00\x00\xc8\x00\x00\x00\x05world'


:code:`construct-classes` support nested structs, but you need to declare them explicitly:

.. code-block:: python

    class LargerStruct(Struct):
        # specify the subclass type:
        basic: BasicStruct = subcon(BasicStruct)
        # in case of a list, specify the item type:
        basic_array: List[BasicStruct] = subcon(BasicStruct)
        # the `subcon()` function supports all arguments of `dataclass.field`:
        default_array: List[BasicStruct] = subcon(BasicStruct, default_factory=list)

        # to refer to the subcon, use the `SUBCON` class attribute:
        SUBCON = c.Struct(
            "basic" / BasicStruct.SUBCON,
            "basic_array" / c.Array(2, BasicStruct.SUBCON),
            "default_array" / c.PrefixedArray(c.Int8ul, BasicStruct.SUBCON),
        )

Use :code:`dataclasses.field()` to specify attributes on fields that are not subcons.

There are currently no other features. In particular, the resulting class is a Python
dataclass, but you cannot specify its parameters like :code:`frozen` etc.


Installing
----------

Install using pip:

    $ pip install construct-classes


Changelog
~~~~~~~~~

See `CHANGELOG.rst`_.

.. _CHANGELOG.rst: https://github.com/matejcik/construct-classes/blob/master/CHANGELOG.rst


Footer
------

* Free software: MIT License

.. * Documentation: https://construct-classes.readthedocs.io.
