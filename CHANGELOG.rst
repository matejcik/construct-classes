Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_, and this project adheres to
`Semantic Versioning`_.

Unreleased
------------

Please see all `Unreleased Changes`_ for more information.

.. _Unreleased Changes: https://github.com/matejcik/construct-classes/compare/v0.2.2...HEAD

0.2.2 - 2025-08-26
--------------------

Removed
~~~~~~~

- Drop support for Pythons 3.9 and older. This was broken in 0.2 and improperly marked
  by the package metadata.

0.2.1 - 2025-08-25
--------------------

Fixed
~~~~~

- Fix exception when creating a subclass of a subclass of :code:`Struct`.


0.2.0 - 2025-08-25
--------------------

Added
~~~~~

- Allow pass-through of dataclass arguments via class attributes.

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Subclasses of :code:`Struct` are now :code:`kw_only` by default. This will break
  any constructor invocations using positional arguments. You can explicitly
  set :code:`kw_only=False` on your :code:`Struct` subclass to restore the old
  behavior.


0.1.2 - 2022-10-07
--------------------

Fixed
~~~~~

- Support for dataclasses that do not contain all the attributes described 
  in :code:`SUBCON`.


0.1.1 - 2022-10-05
------------------

Initial version.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html
