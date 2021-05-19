Welcome to gon's documentation!
===============================

.. contents::
    :local:

.. note::
   If object is not listed in documentation
   it should be considered as implementation detail
   that can change and should not be relied upon.

interfaces
==========

.. autoclass:: gon.base.Geometry
    :members:
    :special-members:
.. autoclass:: gon.base.Compound
    :members:
    :special-members:
.. autoclass:: gon.base.Indexable
    :members:
    :special-members:
.. autoclass:: gon.base.Linear
    :members:
    :special-members:
.. autoclass:: gon.base.Shaped
    :members:
    :special-members:

primitive geometries
====================
.. autoclass:: gon.base.Point
    :members:
    :special-members:

degenerate geometries
=====================
.. autodata:: gon.base.EMPTY
.. autoclass:: gon.base.Empty
    :members:
    :special-members:

discrete geometries
===================
.. autoclass:: gon.base.Multipoint
    :members:
    :special-members:

linear geometries
=================
.. autoclass:: gon.base.Segment
    :members:
    :special-members:
.. autoclass:: gon.base.Multisegment
    :members:
    :special-members:
.. autoclass:: gon.base.Contour
    :members:
    :special-members:

shaped geometries
=================
.. autoclass:: gon.base.Polygon
    :members:
    :special-members:
.. autoclass:: gon.base.Multipolygon
    :members:
    :special-members:

mixed geometries
================
.. autoclass:: gon.base.Mix
    :members:
    :special-members:

enumerations
============
.. autoclass:: gon.base.Location
    :members:
.. autoclass:: gon.base.Orientation
    :members:
.. autoclass:: gon.base.Relation
    :members:

graphs
======
.. autoclass:: gon.base.Triangulation
    :members:
