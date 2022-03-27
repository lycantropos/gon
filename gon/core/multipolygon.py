from functools import partial
from typing import (Optional,
                    Sequence)

from bentley_ottmann.planar import segments_cross_or_overlap
from clipping.planar import (complete_intersect_multipolygons,
                             complete_intersect_multiregions,
                             complete_intersect_multisegment_with_multipolygon,
                             complete_intersect_polygon_with_multipolygon,
                             complete_intersect_region_with_multiregion,
                             complete_intersect_segment_with_multipolygon,
                             subtract_multipolygon_from_multisegment,
                             subtract_multipolygon_from_polygon,
                             subtract_multipolygon_from_segment,
                             subtract_multipolygons,
                             subtract_polygon_from_multipolygon,
                             symmetric_subtract_multipolygon_from_multisegment,
                             symmetric_subtract_multipolygon_from_polygon,
                             symmetric_subtract_multipolygon_from_segment,
                             symmetric_subtract_multipolygons,
                             unite_multipolygons,
                             unite_multisegment_with_multipolygon,
                             unite_polygon_with_multipolygon,
                             unite_segment_with_multipolygon)
from ground.base import Context
from ground.hints import Scalar
from locus import r
from orient.planar import (multipolygon_in_multipolygon,
                           multisegment_in_multipolygon,
                           point_in_multipolygon,
                           polygon_in_multipolygon,
                           segment_in_multipolygon)
from reprit.base import generate_repr

from .angle import Angle
from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation,
                       Shaped)
from .contour import Contour
from .geometry import Geometry
from .iterable import (flatten,
                       non_negative_min)
from .multipoint import Multipoint
from .packing import pack_mix
from .point import Point
from .polygon import Polygon
from .segment import Segment

MIN_MULTIPOLYGON_POLYGONS_COUNT = 2


class Multipolygon(Indexable[Scalar], Shaped[Scalar]):
    __slots__ = '_locate', '_polygons', '_polygons_set'

    def __init__(self, polygons: Sequence[Polygon[Scalar]]) -> None:
        """
        Initializes multipolygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)
        """
        self._polygons, self._polygons_set = polygons, frozenset(polygons)
        self._locate = partial(point_in_multipolygon,
                               multipolygon=self,
                               context=self._context)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns intersection of the multipolygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon & multipolygon == multipolygon
        True
        """
        if isinstance(other, Segment):
            return complete_intersect_segment_with_multipolygon(
                    other, self,
                    context=self._context
            )
        elif isinstance(other, Linear):
            return complete_intersect_multisegment_with_multipolygon(
                    other, self,
                    context=self._context
            )
        else:
            return (self._intersect_with_polygon(other)
                    if isinstance(other, Polygon)
                    else (self._intersect_with_multipolygon(other)
                          if isinstance(other, Multipolygon)
                          else NotImplemented))

    __rand__ = __and__

    def __contains__(self, point: Point[Scalar]) -> bool:
        """
        Checks if the multipolygon contains the point.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> Point(0, 0) in multipolygon
        True
        >>> Point(1, 1) in multipolygon
        True
        >>> Point(2, 2) in multipolygon
        True
        >>> Point(3, 3) in multipolygon
        False
        >>> Point(4, 5) in multipolygon
        True
        >>> Point(5, 6) in multipolygon
        True
        >>> Point(6, 7) in multipolygon
        True
        >>> Point(7, 7) in multipolygon
        False
        """
        return bool(self.locate(point))

    def __eq__(self, other: 'Multipolygon[Scalar]') -> bool:
        """
        Checks if multipolygons are equal.

        Time complexity:
            ``O(len(self.polygons))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon == multipolygon
        True
        """
        return self is other or (self._polygons_set == other._polygons_set
                                 if isinstance(other, Multipolygon)
                                 else NotImplemented)

    def __ge__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the multipolygon is a superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon >= multipolygon
        True
        """
        return (other is self._context.empty
                or self == other
                or (self.relate(other) in (Relation.EQUAL, Relation.COMPONENT,
                                           Relation.ENCLOSED, Relation.WITHIN)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the multipolygon is a strict superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon > multipolygon
        False
        """
        return (other is self._context.empty
                or self != other
                and (self.relate(other) in (Relation.COMPONENT,
                                            Relation.ENCLOSED, Relation.WITHIN)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        """
        Returns hash value of the polygon.

        Time complexity:
            ``O(len(self.polygons))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> hash(multipolygon) == hash(multipolygon)
        True
        """
        return hash(self._polygons_set)

    def __le__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the multipolygon is a subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon <= multipolygon
        True
        """
        return (self == other
                or not isinstance(other, (Multipoint, Linear))
                and (self.relate(other) in (Relation.COVER,
                                            Relation.ENCLOSES,
                                            Relation.COMPOSITE,
                                            Relation.EQUAL)
                     if isinstance(other, Shaped)
                     else NotImplemented))

    def __lt__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the multipolygon is a strict subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon < multipolygon
        False
        """
        return (self != other
                and not isinstance(other, (Multipoint, Linear))
                and (self.relate(other) in (Relation.COVER,
                                            Relation.ENCLOSES,
                                            Relation.COMPOSITE)
                     if isinstance(other, Shaped)
                     else NotImplemented))

    def __or__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns union of the multipolygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon | multipolygon == multipolygon
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (unite_segment_with_multipolygon(other, self,
                                                 context=self._context)
                 if isinstance(other, Segment)
                 else
                 (unite_multisegment_with_multipolygon(other, self,
                                                       context=self._context)
                  if isinstance(other, Linear)
                  else (unite_polygon_with_multipolygon(other, self,
                                                        context=self._context)
                        if isinstance(other, Polygon)
                        else (unite_multipolygons(self, other,
                                                  context=self._context)
                              if isinstance(other, Multipolygon)
                              else NotImplemented)))))

    __ror__ = __or__

    def __rsub__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns difference of the other geometry with the multipolygon.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)
        """
        return (subtract_multipolygon_from_segment(other, self,
                                                   context=self._context)
                if isinstance(other, Segment)
                else
                (subtract_multipolygon_from_multisegment(other, self,
                                                         context=self._context)
                 if isinstance(other, Linear)
                 else
                 (subtract_multipolygon_from_polygon(other, self,
                                                     context=self._context)
                  if isinstance(other, Polygon)
                  else NotImplemented)))

    def __sub__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns difference of the multipolygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import EMPTY, Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon - multipolygon is EMPTY
        True
        """
        return (self
                if isinstance(other, (Linear, Multipoint))
                else
                (subtract_polygon_from_multipolygon(self, other,
                                                    context=self._context)
                 if isinstance(other, Polygon)
                 else (subtract_multipolygons(self, other,
                                              context=self._context)
                       if isinstance(other, Multipolygon)
                       else NotImplemented)))

    def __xor__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns symmetric difference of the multipolygon
        with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import EMPTY, Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon ^ multipolygon is EMPTY
        True
        """
        if isinstance(other, Multipoint):
            return self._unite_with_multipoint(other)
        elif isinstance(other, Segment):
            return symmetric_subtract_multipolygon_from_segment(
                    other, self,
                    context=self._context
            )
        elif isinstance(other, Linear):
            return symmetric_subtract_multipolygon_from_multisegment(
                    other, self,
                    context=self._context
            )
        elif isinstance(other, Polygon):
            return symmetric_subtract_multipolygon_from_polygon(
                    other, self,
                    context=self._context
            )
        else:
            return (symmetric_subtract_multipolygons(self, other,
                                                     context=self._context)
                    if isinstance(other, Multipolygon)
                    else NotImplemented)

    __rxor__ = __xor__

    @property
    def area(self) -> Scalar:
        """
        Returns area of the multipolygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.area == 128
        True
        """
        return sum(polygon.area for polygon in self.polygons)

    @property
    def centroid(self) -> Point[Scalar]:
        """
        Returns centroid of the multipolygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.centroid == Point(7, 7)
        True
        """
        return self._context.multipolygon_centroid(self)

    @property
    def perimeter(self) -> Scalar:
        """
        Returns perimeter of the multipolygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.perimeter == 128
        True
        """
        return sum(polygon.perimeter for polygon in self.polygons)

    @property
    def polygons(self) -> Sequence[Polygon[Scalar]]:
        """
        Returns polygons of the multipolygon.

        Time complexity:
            ``O(polygons_count)``
        Memory complexity:
            ``O(polygons_count)``

        where ``polygons_count = len(self.polygons)``.

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> (multipolygon.polygons
        ...  == [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                       Point(0, 14)]),
        ...              [Contour([Point(2, 2), Point(2, 12), Point(12, 12),
        ...                        Point(12, 2)])]),
        ...      Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                       Point(4, 10)]),
        ...              [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                        Point(8, 6)])])])
        True
        """
        return list(self._polygons)

    def distance_to(self, other: Geometry[Scalar]) -> Scalar:
        """
        Returns distance between the multipolygon and the other geometry.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.distance_to(multipolygon) == 0
        True
        """
        return (self._distance_to_point(other)
                if isinstance(other, Point)
                else
                (non_negative_min(self._distance_to_point(point)
                                  for point in other.points)
                 if isinstance(other, Multipoint)
                 else
                 (self._distance_to_segment(other)
                  if isinstance(other, Segment)
                  else
                  (non_negative_min(self._distance_to_segment(segment)
                                    for segment in other.segments)
                   if isinstance(other, Linear)
                   else
                   (non_negative_min(self._distance_to_segment(edge)
                                     for edge in other.edges)
                    if isinstance(other, Polygon)
                    else ((non_negative_min(self._distance_to_segment(edge)
                                            for polygon in other.polygons
                                            for edge in polygon.edges)
                           if self.disjoint(other)
                           else 0)
                          if isinstance(other, Multipolygon)
                          else other.distance_to(self)))))))

    def index(self) -> None:
        """
        Pre-processes the multipolygon to potentially improve queries.

        Time complexity:
            ``O(vertices_count * log vertices_count)`` expected,
            ``O(vertices_count ** 2)`` worst
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.index()
        """
        polygons = self.polygons
        for polygon in polygons:
            polygon.index()
        context = self._context
        to_polygon_box = context.polygon_box
        tree = r.Tree([to_polygon_box(polygon) for polygon in polygons],
                      context=context)
        self._locate = partial(_locate_point_in_indexed_polygons, polygons,
                               tree,
                               context=context)

    def locate(self, point: Point[Scalar]) -> Location:
        """
        Finds location of the point relative to the multipolygon.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.locate(Point(0, 0)) is Location.BOUNDARY
        True
        >>> multipolygon.locate(Point(1, 1)) is Location.INTERIOR
        True
        >>> multipolygon.locate(Point(2, 2)) is Location.BOUNDARY
        True
        >>> multipolygon.locate(Point(3, 3)) is Location.EXTERIOR
        True
        >>> multipolygon.locate(Point(4, 5)) is Location.BOUNDARY
        True
        >>> multipolygon.locate(Point(5, 6)) is Location.INTERIOR
        True
        >>> multipolygon.locate(Point(6, 7)) is Location.BOUNDARY
        True
        >>> multipolygon.locate(Point(7, 7)) is Location.EXTERIOR
        True
        """
        return self._locate(point)

    def relate(self, other: Compound[Scalar]) -> Relation:
        """
        Finds relation between the multipolygon and the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.relate(multipolygon) is Relation.EQUAL
        True
        """
        return (segment_in_multipolygon(other, self)
                if isinstance(other, Segment)
                else (multisegment_in_multipolygon(other, self)
                      if isinstance(other, Linear)
                      else (polygon_in_multipolygon(other, self)
                            if isinstance(other, Polygon)
                            else (multipolygon_in_multipolygon(other, self)
                                  if isinstance(other, Multipolygon)
                                  else other.relate(self).complement))))

    def rotate(self,
               angle: Angle,
               point: Optional[Point[Scalar]] = None
               ) -> 'Multipolygon[Scalar]':
        """
        Rotates the multipolygon by given angle around given point.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Angle, Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.rotate(Angle(1, 0)) == multipolygon
        True
        >>> (multipolygon.rotate(Angle(0, 1), Point(1, 1))
        ...  == Multipolygon([
        ...          Polygon(Contour([Point(2, 0), Point(2, 14),
        ...                           Point(-12, 14), Point(-12, 0)]),
        ...                  [Contour([Point(0, 2), Point(-10, 2),
        ...                            Point(-10, 12), Point(0, 12)])]),
        ...          Polygon(Contour([Point(-2, 4), Point(-2, 10),
        ...                           Point(-8, 10), Point(-8, 4)]),
        ...                  [Contour([Point(-4, 6), Point(-6, 6),
        ...                            Point(-6, 8), Point(-4, 8)])])]))
        True
        """
        if point is None:
            return self._context.rotate_multipolygon_around_origin(
                    self, angle.cosine, angle.sine
            )
        else:
            return self._context.rotate_multipolygon(self, angle.cosine,
                                                     angle.sine, point)

    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> Compound[Scalar]:
        """
        Scales the multipolygon by given factor.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.scale(1) == multipolygon
        True
        >>> (multipolygon.scale(1, 2)
        ...  == Multipolygon([
        ...          Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 28),
        ...                           Point(0, 28)]),
        ...                  [Contour([Point(2, 4), Point(2, 24),
        ...                            Point(12, 24), Point(12, 4)])]),
        ...          Polygon(Contour([Point(4, 8), Point(10, 8), Point(10, 20),
        ...                           Point(4, 20)]),
        ...                  [Contour([Point(6, 12), Point(6, 16),
        ...                            Point(8, 16), Point(8, 12)])])]))
        True
        """
        return self._context.scale_multipolygon(
                self, factor_x, factor_x if factor_y is None else factor_y
        )

    def translate(self,
                  step_x: Scalar,
                  step_y: Scalar) -> 'Multipolygon[Scalar]':
        """
        Translates the multipolygon by given step.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> (multipolygon.translate(1, 2)
        ...  == Multipolygon([
        ...          Polygon(Contour([Point(1, 2), Point(15, 2), Point(15, 16),
        ...                           Point(1, 16)]),
        ...                  [Contour([Point(3, 4), Point(3, 14),
        ...                            Point(13, 14), Point(13, 4)])]),
        ...          Polygon(Contour([Point(5, 6), Point(11, 6), Point(11, 12),
        ...                           Point(5, 12)]),
        ...                  [Contour([Point(7, 8), Point(7, 10), Point(9, 10),
        ...                            Point(9, 8)])])]))
        True
        """
        return self._context.translate_multipolygon(self, step_x, step_y)

    def validate(self) -> None:
        """
        Checks if the multipolygon is valid.

        Time complexity:
            ``O(vertices_count * log (vertices_count))``
        Memory complexity:
            ``O(vertices_count)``

        where
            
            .. code-block:: python

                vertices_count = sum(len(polygon.border.vertices)
                                     + sum(len(hole.vertices)
                                           for hole in polygon.holes)
                                     for polygon in self.polygons)

        >>> from gon.base import Contour, Multipolygon, Point, Polygon
        >>> multipolygon = Multipolygon(
        ...         [Polygon(Contour([Point(0, 0), Point(14, 0), Point(14, 14),
        ...                           Point(0, 14)]),
        ...                  [Contour([Point(2, 2), Point(2, 12),
        ...                            Point(12, 12), Point(12, 2)])]),
        ...          Polygon(Contour([Point(4, 4), Point(10, 4), Point(10, 10),
        ...                           Point(4, 10)]),
        ...                  [Contour([Point(6, 6), Point(6, 8), Point(8, 8),
        ...                            Point(8, 6)])])])
        >>> multipolygon.validate()
        """
        if len(self.polygons) < MIN_MULTIPOLYGON_POLYGONS_COUNT:
            raise ValueError('Multipolygon should have '
                             'at least {min_size} polygons, '
                             'but found {size}.'
                             .format(min_size=MIN_MULTIPOLYGON_POLYGONS_COUNT,
                                     size=len(self.polygons)))
        elif len(self.polygons) > len(self._polygons_set):
            raise ValueError('Duplicate polygons found.')
        for polygon in self.polygons:
            polygon.validate()
        if segments_cross_or_overlap(
                list(flatten(polygon.edges for polygon in self.polygons)),
                context=self._context
        ):
            raise ValueError('Polygons should only touch each other '
                             'in discrete number of points.')

    def _as_multiregion(self) -> Sequence[Contour[Scalar]]:
        return [polygon.border for polygon in self.polygons]

    def _distance_to_point(self, other: Point[Scalar]) -> Scalar:
        return non_negative_min(polygon._distance_to_point(other)
                                for polygon in self.polygons)

    def _distance_to_segment(self, other: Segment[Scalar]) -> Scalar:
        return non_negative_min(polygon._distance_to_segment(other)
                                for polygon in self.polygons)

    def _intersect_with_multipolygon(self, other: 'Multipolygon[Scalar]'
                                     ) -> Compound[Scalar]:
        return (complete_intersect_multipolygons(self, other,
                                                 context=self._context)
                if (_multipolygon_has_holes(self)
                    or _multipolygon_has_holes(other))
                else complete_intersect_multiregions(self._as_multiregion(),
                                                     other._as_multiregion(),
                                                     context=self._context))

    def _intersect_with_polygon(self, other: Polygon[Scalar]
                                ) -> Compound[Scalar]:
        if _multipolygon_has_holes(self) or other.holes:
            return complete_intersect_polygon_with_multipolygon(
                    other, self,
                    context=self._context
            )
        else:
            return complete_intersect_region_with_multiregion(
                    other.border, self._as_multiregion(),
                    context=self._context
            )

    def _unite_with_multipoint(self, other: Multipoint[Scalar]
                               ) -> Compound[Scalar]:
        context = self._context
        return pack_mix(other - self, context.empty, self, context.empty,
                        context.mix_cls)


def _locate_point_in_indexed_polygons(polygons: Sequence[Polygon],
                                      tree: r.Tree,
                                      point: Point,
                                      context: Context) -> Location:
    candidates_indices = tree.find_supersets_indices(
            context.box_cls(point.x, point.x, point.y, point.y)
    )
    for candidate_index in candidates_indices:
        location = polygons[candidate_index].locate(point)
        if location is not Location.EXTERIOR:
            return location
    return Location.EXTERIOR


def _multipolygon_has_holes(multipolygon: Multipolygon) -> bool:
    return any(polygon.holes for polygon in multipolygon.polygons)
