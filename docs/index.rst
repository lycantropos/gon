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
    :special-members:
    :inherited-members:

degenerate geometries
=====================
.. autodata:: gon.base.EMPTY
.. autoclass:: gon.base.Empty
    :special-members:
    :inherited-members:

discrete geometries
===================
.. autoclass:: gon.base.Multipoint
    :special-members:
    :inherited-members:

linear geometries
=================
.. autoclass:: gon.base.Segment
    :special-members:
    :inherited-members:
.. autoclass:: gon.base.Multisegment
    :special-members:
    :inherited-members:
.. autoclass:: gon.base.Contour
    :special-members:
    :inherited-members:

shaped geometries
=================
.. autoclass:: gon.base.Polygon
    :special-members:
    :inherited-members:
.. autoclass:: gon.base.Multipolygon
    :special-members:
    :inherited-members:

mixed geometries
================
.. autoclass:: gon.base.Mix
    :special-members:
    :inherited-members:

helper geometric objects
========================
.. autoclass:: gon.base.Angle
    :special-members:
    :inherited-members:

.. autoclass:: gon.base.Vector
    :special-members:
    :inherited-members:

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
