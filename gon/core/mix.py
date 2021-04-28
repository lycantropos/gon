from typing import Optional

from reprit.base import generate_repr

from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation,
                       Shaped)
from .empty import (EMPTY,
                    Maybe)
from .geometry import Geometry
from .hints import Coordinate
from .iterable import non_negative_min
from .multipoint import Multipoint
from .multipolygon import Multipolygon
from .point import Point

MIN_MIX_NON_EMPTY_COMPONENTS = 2


class Mix(Indexable):
    __slots__ = '_components', '_linear', '_multipoint', '_shaped'

    def __init__(self,
                 multipoint: Maybe[Multipoint],
                 linear: Maybe[Linear],
                 shaped: Maybe[Shaped]) -> None:
        """
        Initializes mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._components = self._multipoint, self._linear, self._shaped = (
            multipoint, linear, shaped)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the mix with the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix & mix == mix
        True
        """
        multipoint_part = self.multipoint & other
        linear_part = self.linear & other
        shaped_part = self.shaped & other
        if isinstance(linear_part, Multipoint):
            shaped_part |= linear_part
            linear_part = EMPTY
        elif isinstance(linear_part, Mix):
            shaped_part |= linear_part.multipoint
            linear_part = linear_part.linear
        if isinstance(shaped_part, Multipoint):
            linear_part |= shaped_part
            if isinstance(linear_part, Mix):
                multipoint_part |= linear_part.multipoint
                linear_part = linear_part.linear
            shaped_part = EMPTY
        elif isinstance(shaped_part, Linear):
            linear_part |= shaped_part
            shaped_part = EMPTY
        elif isinstance(shaped_part, Mix):
            linear_part = (linear_part | shaped_part.linear
                           | shaped_part.multipoint)
            shaped_part = shaped_part.shaped
        if isinstance(linear_part, Multipoint):
            multipoint_part |= linear_part
            linear_part = EMPTY
        elif isinstance(linear_part, Mix):
            multipoint_part |= linear_part.multipoint
            linear_part = linear_part.linear
        return from_mix_components(multipoint_part, linear_part, shaped_part)

    __rand__ = __and__

    def __contains__(self, point: Point) -> bool:
        """
        Returns intersection of the mix with the other geometry.

        Time complexity:
            ``O(log elements_count)`` expected after indexing,
            ``O(elements_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> Point(0, 0) in mix
        True
        >>> Point(1, 1) in mix
        True
        >>> Point(2, 2) in mix
        True
        >>> Point(3, 3) in mix
        True
        >>> Point(4, 3) in mix
        True
        >>> Point(5, 2) in mix
        True
        >>> Point(6, 1) in mix
        True
        >>> Point(7, 0) in mix
        False
        """
        return bool(self.locate(point))

    def __eq__(self, other: Geometry) -> bool:
        """
        Checks if mixes are equal.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix == mix
        True
        """
        return self is other or (isinstance(other, Mix)
                                 and self._components == other._components
                                 if isinstance(other, Geometry)
                                 else NotImplemented)

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the mix is a superset of the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix >= mix
        True
        """
        return (other is EMPTY
                or self == other
                or ((self.shaped is not EMPTY
                     or not isinstance(other, Shaped)
                     and (not isinstance(other, Mix)
                          or other.shaped is EMPTY))
                    and self.relate(other) in (Relation.EQUAL,
                                               Relation.COMPONENT,
                                               Relation.ENCLOSED,
                                               Relation.WITHIN)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the mix is a strict superset of the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix > mix
        False
        """
        return (other is EMPTY
                or self != other
                and ((self.shaped is not EMPTY
                      or not isinstance(other, Shaped)
                      and (not isinstance(other, Mix)
                           or other.shaped is EMPTY))
                     and self.relate(other) in (Relation.COMPONENT,
                                                Relation.ENCLOSED,
                                                Relation.WITHIN)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        """
        Returns hash value of the mix.

        Time complexity:
            ``O(components_size)``
        Memory complexity:
            ``O(1)``

        where ``components_size = multipoint_size + multisegment_size\
 + multipolygon_size``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_size = len(polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> hash(mix) == hash(mix)
        True
        """
        return hash(self._components)

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the mix is a subset of the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix <= mix
        True
        """
        return (self == other
                or (not isinstance(other, Multipoint)
                    and (self.shaped is EMPTY
                         or not isinstance(other, Linear)
                         and (not isinstance(other, Mix)
                              or other.shaped is not EMPTY))
                    and self.relate(other) in (Relation.COVER,
                                               Relation.ENCLOSES,
                                               Relation.COMPOSITE,
                                               Relation.EQUAL)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the mix is a strict subset of the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix < mix
        False
        """
        return (self != other
                and (not isinstance(other, Multipoint)
                     and (self.shaped is EMPTY
                          or not isinstance(other, Linear)
                          and (not isinstance(other, Mix)
                               or other.shaped is not EMPTY))
                     and self.relate(other) in (Relation.COVER,
                                                Relation.ENCLOSES,
                                                Relation.COMPOSITE)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the mix with the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix | mix == mix
        True
        """
        if isinstance(other, Multipoint):
            return Mix(self.multipoint | (other - self.shaped - self.linear),
                       self.linear, self.shaped)
        elif isinstance(other, Linear):
            multipoint_part, linear_part = self.multipoint, self.linear
            shaped_part = self.shaped | other
            if isinstance(shaped_part, Linear):
                linear_part = linear_part | shaped_part | multipoint_part
                shaped_part = EMPTY
            elif isinstance(shaped_part, Mix):
                linear_part = (linear_part | shaped_part.linear
                               | multipoint_part)
                shaped_part = shaped_part.shaped
            else:
                # other is subset of the shaped component
                return from_mix_components(multipoint_part, linear_part,
                                           shaped_part)
            if isinstance(linear_part, Mix):
                multipoint_part, linear_part = (linear_part.multipoint,
                                                linear_part.linear)
            else:
                multipoint_part = EMPTY
            return from_mix_components(multipoint_part, linear_part,
                                       shaped_part)
        elif isinstance(other, (Shaped, Mix)):
            return self.shaped | other | self.linear | self.multipoint
        else:
            return NotImplemented

    __ror__ = __or__

    def __rsub__(self, other: Compound) -> Compound:
        """
        Returns difference of the other geometry with the mix.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.
        """
        return ((other - self.multipoint) & (other - self.linear)
                & other - self.shaped)

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the mix with the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix - mix is EMPTY
        True
        """
        return from_mix_components(self.multipoint - other,
                                   self.linear - other, self.shaped - other)

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the mix with the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix ^ mix is EMPTY
        True
        """
        if isinstance(other, Multipoint):
            rest_other = other - self.shaped - self.linear
            return from_mix_components(self.multipoint ^ rest_other,
                                       self.linear, self.shaped)
        elif isinstance(other, Linear):
            multipoint_part, linear_part = self.multipoint, self.linear
            shaped_part = self.shaped ^ other
            if isinstance(shaped_part, Linear):
                linear_part = linear_part ^ shaped_part ^ multipoint_part
                shaped_part = EMPTY
            elif isinstance(shaped_part, Mix):
                linear_part = (linear_part ^ shaped_part.linear
                               ^ multipoint_part)
                shaped_part = shaped_part.shaped
            else:
                # other is subset of the shaped component
                return from_mix_components(multipoint_part, linear_part,
                                           shaped_part)
            if isinstance(linear_part, Mix):
                multipoint_part, linear_part = (linear_part.multipoint,
                                                linear_part.linear)
            else:
                multipoint_part = EMPTY
            return from_mix_components(multipoint_part, linear_part,
                                       shaped_part)
        elif isinstance(other, (Shaped, Mix)):
            return self.shaped ^ other ^ self.linear ^ self.multipoint
        else:
            return NotImplemented

    __rxor__ = __xor__

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the mix.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multisegment_size\
 if self.shaped is EMPTY else multipolygon_vertices_count``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.centroid == Point(3, 3)
        True
        """
        return (self.linear if self.shaped is EMPTY else self.shaped).centroid

    @property
    def multipoint(self) -> Maybe[Multipoint]:
        """
        Returns multipoint of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.multipoint == Multipoint([Point(3, 3)])
        True
        """
        return self._multipoint

    @property
    def shaped(self) -> Maybe[Shaped]:
        """
        Returns shaped component of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> from gon.base import Contour
        >>> mix.shaped == Polygon(Contour([Point(0, 0), Point(6, 0),
        ...                                Point(6, 6), Point(0, 6)]),
        ...                       [Contour([Point(2, 2), Point(2, 4),
        ...                                 Point(4, 4), Point(4, 2)])])
        True
        """
        return self._shaped

    @property
    def linear(self) -> Maybe[Linear]:
        """
        Returns linear component of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.linear == Segment(Point(6, 6), Point(6, 8))
        True
        """
        return self._linear

    def distance_to(self, other: Geometry) -> Coordinate:
        """
        Returns distance between the mix and the other geometry.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multisegment_size +\
 multipolygon_vertices_count``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.distance_to(mix) == 0
        True
        """
        return non_negative_min(component.distance_to(other)
                                for component in self._components
                                if component is not EMPTY)

    def index(self) -> None:
        """
        Pre-processes the mix to potentially improve queries.

        Time complexity:
            ``O(elements_count * log elements_count)`` expected,
            ``O(elements_count ** 2)`` worst
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multisegment_size +\
 multipolygon_vertices_count``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.index()
        """
        if isinstance(self.multipoint, Indexable):
            self.multipoint.index()
        if isinstance(self.linear, Indexable):
            self.linear.index()
        if isinstance(self.shaped, Indexable):
            self.shaped.index()

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the mix.

        Time complexity:
            ``O(log elements_count)`` expected after indexing,
            ``O(elements_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.locate(Point(0, 0)) is Location.BOUNDARY
        True
        >>> mix.locate(Point(1, 1)) is Location.INTERIOR
        True
        >>> mix.locate(Point(2, 2)) is Location.BOUNDARY
        True
        >>> mix.locate(Point(3, 3)) is Location.BOUNDARY
        True
        >>> mix.locate(Point(4, 3)) is Location.BOUNDARY
        True
        >>> mix.locate(Point(5, 2)) is Location.INTERIOR
        True
        >>> mix.locate(Point(6, 1)) is Location.BOUNDARY
        True
        >>> mix.locate(Point(7, 0)) is Location.EXTERIOR
        True
        """
        for candidate in self._components:
            location = candidate.locate(point)
            if location is not Location.EXTERIOR:
                return location
        return Location.EXTERIOR

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the mix and the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.relate(mix) is Relation.EQUAL
        True
        """
        return (self._relate_multipoint(other)
                if isinstance(other, Multipoint)
                else (self._relate_linear(other)
                      if isinstance(other, Linear)
                      else (self._relate_shaped(other)
                            if isinstance(other, Shaped)
                            else (self._relate_mix(other)
                                  if isinstance(other, Mix)
                                  else other.relate(self).complement))))

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional[Point] = None) -> 'Mix':
        """
        Rotates the mix by given cosine & sine around given point.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.rotate(1, 0) == mix
        True
        >>> (mix.rotate(0, 1, Point(1, 1))
        ...  == Mix(Multipoint([Point(-1, 3)]),
        ...         Segment(Point(-4, 6), Point(-6, 6)),
        ...         Polygon(Contour([Point(2, 0), Point(2, 6), Point(-4, 6),
        ...                          Point(-4, 0)]),
        ...                 [Contour([Point(0, 2), Point(-2, 2), Point(-2, 4),
        ...                           Point(0, 4)])])))
        True
        """
        return Mix(self.multipoint.rotate(cosine, sine, point),
                   self.linear.rotate(cosine, sine, point),
                   self.shaped.rotate(cosine, sine, point))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> Compound:
        """
        Scales the mix by given factor.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.scale(1) == mix
        True
        >>> (mix.scale(1, 2)
        ...  == Mix(Multipoint([Point(3, 6)]),
        ...         Segment(Point(6, 12), Point(6, 16)),
        ...         Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 12),
        ...                          Point(0, 12)]),
        ...                 [Contour([Point(2, 4), Point(2, 8), Point(4, 8),
        ...                           Point(4, 4)])])))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        return (Mix(self.multipoint.scale(factor_x, factor_y),
                    self.linear.scale(factor_x, factor_y),
                    self.shaped.scale(factor_x, factor_y))
                if factor_x and factor_y
                else ((self.multipoint.scale(factor_x, factor_y)
                       | self.linear.scale(factor_x, factor_y)
                       | self.shaped.scale(factor_x, factor_y))
                      if factor_x or factor_y
                      else Multipoint([Point(factor_x, factor_y)])))

    def translate(self, step_x: Coordinate, step_y: Coordinate) -> 'Mix':
        """
        Translates the mix by given step.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> (mix.translate(1, 2)
        ...  == Mix(Multipoint([Point(4, 5)]),
        ...         Segment(Point(7, 8), Point(7, 10)),
        ...         Polygon(Contour([Point(1, 2), Point(7, 2), Point(7, 8),
        ...                          Point(1, 8)]),
        ...                 [Contour([Point(3, 4), Point(3, 6), Point(5, 6),
        ...                           Point(5, 4)])])))
        True
        """
        return Mix(self.multipoint.translate(step_x, step_y),
                   self.linear.translate(step_x, step_y),
                   self.shaped.translate(step_x, step_y))

    def validate(self) -> None:
        """
        Checks if the mix is valid.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where ``elements_count = multipoint_size + multisegment_size\
 + multipolygon_vertices_count``,
        ``multipoint_size = len(points)``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``points = [] if self.multipoint is EMPTY\
 else self.multipoint.points``,
        ``segments = [] if self.linear is EMPTY else self.linear.segments``,
        ``polygons = [] if self.shaped is EMPTY else self.shaped.polygons``.

        >>> from gon.base import Contour, Polygon, Segment
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.validate()
        """
        if (sum(component is not EMPTY for component in self._components)
                < MIN_MIX_NON_EMPTY_COMPONENTS):
            raise ValueError('At least {count} components should not be empty.'
                             .format(count=MIN_MIX_NON_EMPTY_COMPONENTS))
        for component in self._components:
            component.validate()
        if (not self.multipoint.disjoint(self.linear)
                or not self.multipoint.disjoint(self.shaped)):
            raise ValueError('Multipoint should be disjoint '
                             'with other components.')
        shaped_linear_relation = self.shaped.relate(self.linear)
        if shaped_linear_relation in (Relation.CROSS, Relation.COMPONENT,
                                      Relation.ENCLOSED, Relation.WITHIN):
            raise ValueError('Linear component should not {} shaped component.'
                             .format('cross'
                                     if (shaped_linear_relation
                                         is Relation.CROSS)
                                     else 'be subset of'))
        elif (shaped_linear_relation is Relation.TOUCH
              and any(polygon.border.relate(self.linear)
                      in (Relation.OVERLAP,
                          Relation.COMPOSITE)
                      or any(hole.relate(self.linear)
                             in (Relation.OVERLAP,
                                 Relation.COMPOSITE)
                             for hole in polygon.holes)
                      for polygon in (self.shaped.polygons
                                      if isinstance(self.shaped, Multipolygon)
                                      else [self.shaped]))):
            raise ValueError('Linear component should not overlap '
                             'shaped component borders.')

    def _relate_linear(self, other: Linear) -> Relation:
        if self.shaped is EMPTY:
            multisegment_relation = self.linear.relate(other)
            if multisegment_relation is Relation.DISJOINT:
                multipoint_relation = self.multipoint.relate(other)
                return (Relation.TOUCH
                        if multipoint_relation is Relation.COMPOSITE
                        else multipoint_relation)
            elif multisegment_relation is Relation.COMPOSITE:
                multipoint_relation = self.multipoint.relate(other)
                return (multisegment_relation
                        if multipoint_relation is multisegment_relation
                        else Relation.OVERLAP)
            else:
                return (Relation.COMPONENT
                        if multisegment_relation is Relation.EQUAL
                        else multisegment_relation)
        else:
            multipolygon_relation = self.shaped.relate(other)
            if multipolygon_relation is Relation.DISJOINT:
                multisegment_relation = self.linear.relate(other)
                if multisegment_relation is Relation.DISJOINT:
                    multipoint_relation = self.multipoint.relate(other)
                    return (Relation.TOUCH
                            if multipoint_relation is Relation.COMPOSITE
                            else multipoint_relation)
                elif multisegment_relation in (Relation.TOUCH,
                                               Relation.CROSS,
                                               Relation.COMPONENT):
                    return multisegment_relation
                else:
                    return (Relation.COMPONENT
                            if multisegment_relation is Relation.EQUAL
                            else Relation.TOUCH)
            elif (multipolygon_relation is Relation.TOUCH
                  or multipolygon_relation is Relation.CROSS):
                rest_other = other - self.shaped
                multisegment_relation = self.linear.relate(rest_other)
                return (Relation.COMPONENT
                        if (multisegment_relation is Relation.EQUAL
                            or multisegment_relation is Relation.COMPONENT)
                        else multipolygon_relation)
            else:
                return multipolygon_relation

    def _relate_mix(self, other: 'Mix') -> Relation:
        if self.shaped is other.shaped is EMPTY:
            linear_components_relation = self.linear.relate(other.linear)
            if linear_components_relation is Relation.DISJOINT:
                return (linear_components_relation
                        if (self._relate_multipoint(other.multipoint)
                            is other._relate_multipoint(self.multipoint)
                            is linear_components_relation)
                        else Relation.TOUCH)
            elif linear_components_relation is Relation.COMPOSITE:
                multipoint_relation = other._relate_multipoint(self.multipoint)
                return (linear_components_relation
                        if multipoint_relation is Relation.COMPONENT
                        else Relation.OVERLAP)
            elif linear_components_relation is Relation.EQUAL:
                other_multipoint_relation = self.multipoint.relate(
                        other.multipoint)
                return (Relation.OVERLAP
                        if other_multipoint_relation is Relation.DISJOINT
                        else other_multipoint_relation)
            elif linear_components_relation is Relation.COMPONENT:
                other_multipoint_relation = self._relate_multipoint(
                        other.multipoint)
                return (linear_components_relation
                        if other_multipoint_relation is Relation.COMPONENT
                        else Relation.OVERLAP)
            else:
                return linear_components_relation
        elif self.shaped is EMPTY:
            linear_relation = other._relate_linear(self.linear)
            if linear_relation is Relation.CROSS:
                return linear_relation
            multipoint_relation = other._relate_multipoint(self.multipoint)
            if linear_relation is Relation.DISJOINT:
                return (multipoint_relation
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else (Relation.TOUCH
                              if multipoint_relation is Relation.COMPONENT
                              else Relation.CROSS))
            elif linear_relation is Relation.TOUCH:
                return (Relation.CROSS
                        if multipoint_relation in (Relation.CROSS,
                                                   Relation.ENCLOSED,
                                                   Relation.WITHIN)
                        else linear_relation)
            elif linear_relation is Relation.COMPONENT:
                return (Relation.TOUCH
                        if multipoint_relation is Relation.DISJOINT
                        else (multipoint_relation
                              if (multipoint_relation is Relation.TOUCH
                                  or multipoint_relation is Relation.CROSS)
                              else
                              (Relation.COMPOSITE
                               if multipoint_relation is Relation.COMPONENT
                               else Relation.ENCLOSES)))
            else:
                return (Relation.CROSS
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else (Relation.COVER
                              if multipoint_relation is Relation.WITHIN
                              else Relation.ENCLOSES))
        elif other.shaped is EMPTY:
            other_linear_relation = self._relate_linear(other.linear)
            if other_linear_relation is Relation.CROSS:
                return other_linear_relation
            other_multipoint_relation = self._relate_multipoint(
                    other.multipoint)
            if other_linear_relation is Relation.DISJOINT:
                return (other_multipoint_relation
                        if other_multipoint_relation in (Relation.DISJOINT,
                                                         Relation.TOUCH,
                                                         Relation.CROSS)
                        else
                        (Relation.TOUCH
                         if other_multipoint_relation is Relation.COMPONENT
                         else Relation.CROSS))
            elif other_linear_relation is Relation.TOUCH:
                return (Relation.CROSS
                        if other_multipoint_relation in (Relation.CROSS,
                                                         Relation.ENCLOSED,
                                                         Relation.WITHIN)
                        else other_linear_relation)
            elif other_linear_relation is Relation.COMPONENT:
                return (Relation.TOUCH
                        if (other_multipoint_relation is Relation.DISJOINT
                            or other_multipoint_relation is Relation.TOUCH)
                        else (other_multipoint_relation
                              if (other_multipoint_relation is Relation.CROSS
                                  or (other_multipoint_relation
                                      is Relation.COMPONENT))
                              else Relation.ENCLOSED))
            elif other_linear_relation is Relation.ENCLOSED:
                return (Relation.CROSS
                        if other_multipoint_relation in (Relation.DISJOINT,
                                                         Relation.TOUCH,
                                                         Relation.CROSS)
                        else other_linear_relation)
            else:
                return (Relation.CROSS
                        if other_multipoint_relation in (Relation.DISJOINT,
                                                         Relation.TOUCH,
                                                         Relation.CROSS)
                        else
                        (Relation.ENCLOSED
                         if other_multipoint_relation is Relation.COMPONENT
                         else other_linear_relation))
        shaped_components_relation = self.shaped.relate(other.shaped)
        if (shaped_components_relation is Relation.DISJOINT
                or shaped_components_relation is Relation.TOUCH):
            if self.linear is other.linear is EMPTY:
                other_multipoint_relation = self._relate_multipoint(
                        other.multipoint)
                if other_multipoint_relation is Relation.CROSS:
                    return other_multipoint_relation
                elif (other_multipoint_relation is Relation.ENCLOSED
                      or other_multipoint_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    multipoint_relation = other._relate_multipoint(
                            self.multipoint)
                    if (multipoint_relation
                            is other_multipoint_relation
                            is Relation.DISJOINT):
                        return shaped_components_relation
                    elif multipoint_relation is Relation.CROSS:
                        return multipoint_relation
                    elif (multipoint_relation is Relation.ENCLOSED
                          or multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    else:
                        return Relation.TOUCH
            elif self.linear is EMPTY:
                other_linear_relation = self._relate_linear(other.linear)
                if other_linear_relation is Relation.CROSS:
                    return other_linear_relation
                elif (other_linear_relation is Relation.ENCLOSED
                      or other_linear_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    multipoint_relation = other._relate_multipoint(
                            self.multipoint)
                    if multipoint_relation is Relation.CROSS:
                        return multipoint_relation
                    elif (multipoint_relation is Relation.ENCLOSED
                          or multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif other.multipoint is EMPTY:
                        return (shaped_components_relation
                                if (multipoint_relation
                                    is other_linear_relation
                                    is Relation.DISJOINT)
                                else Relation.TOUCH)
                    else:
                        other_multipoint_relation = self._relate_multipoint(
                                other.multipoint)
                        if other_multipoint_relation is Relation.CROSS:
                            return other_multipoint_relation
                        elif (other_multipoint_relation is Relation.ENCLOSED
                              or other_multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        elif (multipoint_relation
                              is other_multipoint_relation
                              is other_linear_relation
                              is Relation.DISJOINT):
                            return shaped_components_relation
                        else:
                            return Relation.TOUCH
            elif other.linear is EMPTY:
                linear_relation = other._relate_linear(self.linear)
                if linear_relation is Relation.CROSS:
                    return linear_relation
                elif (linear_relation is Relation.ENCLOSED
                      or linear_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    other_multipoint_relation = self._relate_multipoint(
                            other.multipoint)
                    if other_multipoint_relation is Relation.CROSS:
                        return other_multipoint_relation
                    elif (other_multipoint_relation is Relation.ENCLOSED
                          or other_multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif self.multipoint is EMPTY:
                        return (shaped_components_relation
                                if (linear_relation
                                    is other_multipoint_relation
                                    is Relation.DISJOINT)
                                else Relation.TOUCH)
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self.multipoint)
                        if multipoint_relation is Relation.CROSS:
                            return multipoint_relation
                        elif (multipoint_relation is Relation.ENCLOSED
                              or multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        elif (multipoint_relation
                              is linear_relation
                              is other_multipoint_relation
                              is Relation.DISJOINT):
                            return shaped_components_relation
                        else:
                            return Relation.TOUCH
            else:
                other_linear_relation = self._relate_linear(other.linear)
                if other_linear_relation is Relation.CROSS:
                    return other_linear_relation
                elif (other_linear_relation is Relation.ENCLOSED
                      or other_linear_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    linear_relation = other._relate_linear(self.linear)
                    if linear_relation is Relation.CROSS:
                        return linear_relation
                    elif (linear_relation is Relation.ENCLOSED
                          or linear_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif self.multipoint is EMPTY:
                        other_multipoint_relation = self._relate_multipoint(
                                other.multipoint)
                        return (other_multipoint_relation
                                if other_multipoint_relation is Relation.CROSS
                                else
                                (Relation.CROSS
                                 if (other_multipoint_relation
                                     is Relation.ENCLOSED
                                     or other_multipoint_relation
                                     is Relation.WITHIN)
                                 else (shaped_components_relation
                                       if (other_multipoint_relation
                                           is linear_relation
                                           is other_linear_relation
                                           is Relation.DISJOINT)
                                       else Relation.TOUCH)))
                    elif other.multipoint is EMPTY:
                        multipoint_relation = other._relate_multipoint(
                                self.multipoint)
                        return (multipoint_relation
                                if multipoint_relation is Relation.CROSS
                                else
                                (Relation.CROSS
                                 if (multipoint_relation is Relation.ENCLOSED
                                     or multipoint_relation is Relation.WITHIN)
                                 else (shaped_components_relation
                                       if (multipoint_relation
                                           is linear_relation
                                           is other_linear_relation
                                           is Relation.DISJOINT)
                                       else Relation.TOUCH)))
                    else:
                        other_multipoint_relation = self._relate_multipoint(
                                other.multipoint)
                        if other_multipoint_relation is Relation.CROSS:
                            return other_multipoint_relation
                        elif (other_multipoint_relation is Relation.ENCLOSED
                              or other_multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        else:
                            multipoint_relation = other._relate_multipoint(
                                    self.multipoint)
                            return (multipoint_relation
                                    if multipoint_relation is Relation.CROSS
                                    else (Relation.CROSS
                                          if (multipoint_relation
                                              is Relation.ENCLOSED
                                              or multipoint_relation
                                              is Relation.WITHIN)
                                          else
                                          (shaped_components_relation
                                           if (multipoint_relation
                                               is linear_relation
                                               is other_multipoint_relation
                                               is other_linear_relation
                                               is Relation.DISJOINT)
                                           else Relation.TOUCH)))
        elif shaped_components_relation in (Relation.COVER,
                                            Relation.ENCLOSES,
                                            Relation.COMPOSITE):
            if self.linear is EMPTY:
                multipoint_relation = other._relate_multipoint(
                        self.multipoint).complement
                return (shaped_components_relation
                        if multipoint_relation is shaped_components_relation
                        else (Relation.ENCLOSES
                              if multipoint_relation in (Relation.COVER,
                                                         Relation.ENCLOSES,
                                                         Relation.COMPOSITE)
                              else Relation.OVERLAP))
            else:
                linear_relation = other._relate_linear(self.linear).complement
                if linear_relation is shaped_components_relation:
                    if self.multipoint is EMPTY:
                        return shaped_components_relation
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self.multipoint).complement
                        return (shaped_components_relation
                                if (multipoint_relation
                                    is shaped_components_relation)
                                else
                                (Relation.ENCLOSES
                                 if multipoint_relation in (Relation.COVER,
                                                            Relation.ENCLOSES,
                                                            Relation.COMPOSITE)
                                 else Relation.OVERLAP))
                elif linear_relation in (Relation.COVER,
                                         Relation.ENCLOSES,
                                         Relation.COMPOSITE):
                    if self.multipoint is EMPTY:
                        return Relation.ENCLOSES
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self.multipoint).complement
                        return (Relation.ENCLOSES
                                if multipoint_relation in (Relation.COVER,
                                                           Relation.ENCLOSES,
                                                           Relation.COMPOSITE)
                                else Relation.OVERLAP)
                else:
                    return Relation.OVERLAP
        elif shaped_components_relation is Relation.EQUAL:
            linear_components_relation = self.linear.relate(other.linear)
            if self.linear is other.linear is EMPTY:
                multipoints_relation = self.multipoint.relate(other.multipoint)
                return (shaped_components_relation
                        if (self.multipoint is other.multipoint is EMPTY
                            or multipoints_relation is Relation.EQUAL)
                        else
                        (multipoints_relation
                         if (multipoints_relation is Relation.COMPOSITE
                             or multipoints_relation is Relation.COMPONENT)
                         else Relation.OVERLAP))
            elif self.linear is EMPTY:
                multipoints_relation = other._relate_multipoint(
                        self.multipoint)
                return (Relation.COMPOSITE
                        if (multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            elif other.linear is EMPTY:
                multipoints_relation = self._relate_multipoint(
                        other.multipoint)
                return (Relation.COMPONENT
                        if (multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            elif linear_components_relation is Relation.COMPOSITE:
                multipoints_relation = other._relate_multipoint(
                        self.multipoint)
                return (linear_components_relation
                        if (self.multipoint is EMPTY
                            or multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            elif linear_components_relation is Relation.EQUAL:
                multipoints_relation = self.multipoint.relate(other.multipoint)
                return (shaped_components_relation
                        if (self.multipoint is other.multipoint is EMPTY
                            or multipoints_relation is Relation.EQUAL)
                        else
                        (Relation.COMPOSITE
                         if self.multipoint is EMPTY
                         else
                         (Relation.COMPONENT
                          if other.multipoint is EMPTY
                          else
                          (multipoints_relation
                           if (multipoints_relation is Relation.COMPONENT
                               or multipoints_relation is Relation.COMPOSITE)
                           else Relation.OVERLAP))))
            elif linear_components_relation is Relation.COMPONENT:
                multipoints_relation = self._relate_multipoint(
                        other.multipoint)
                return (linear_components_relation
                        if (other.multipoint is EMPTY
                            or multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            else:
                return Relation.OVERLAP
        elif shaped_components_relation in (Relation.COMPONENT,
                                            Relation.ENCLOSED,
                                            Relation.WITHIN):
            if other.linear is EMPTY:
                multipoint_relation = self._relate_multipoint(other.multipoint)
                return (shaped_components_relation
                        if multipoint_relation is shaped_components_relation
                        else (Relation.ENCLOSED
                              if multipoint_relation in (Relation.COMPONENT,
                                                         Relation.ENCLOSED,
                                                         Relation.WITHIN)
                              else Relation.OVERLAP))
            else:
                linear_relation = self._relate_linear(other.linear)
                if linear_relation is shaped_components_relation:
                    if other.multipoint is EMPTY:
                        return shaped_components_relation
                    else:
                        multipoint_relation = self._relate_multipoint(
                                other.multipoint)
                        return (shaped_components_relation
                                if (multipoint_relation
                                    is shaped_components_relation)
                                else
                                (Relation.ENCLOSED
                                 if multipoint_relation in (Relation.COMPONENT,
                                                            Relation.ENCLOSED,
                                                            Relation.WITHIN)
                                 else Relation.OVERLAP))
                elif linear_relation in (Relation.COMPONENT,
                                         Relation.ENCLOSED,
                                         Relation.WITHIN):
                    if other.multipoint is EMPTY:
                        return Relation.ENCLOSED
                    else:
                        multipoint_relation = self._relate_multipoint(
                                other.multipoint)
                        return (Relation.ENCLOSED
                                if multipoint_relation in (Relation.COMPONENT,
                                                           Relation.ENCLOSED,
                                                           Relation.WITHIN)
                                else Relation.OVERLAP)
                else:
                    return Relation.OVERLAP
        else:
            return shaped_components_relation

    def _relate_multipoint(self, other: Multipoint) -> Relation:
        if self.shaped is EMPTY:
            multisegment_relation = self.linear.relate(other)
            if multisegment_relation is Relation.DISJOINT:
                multipoint_relation = self.multipoint.relate(other)
                return (multipoint_relation
                        if multipoint_relation is Relation.DISJOINT
                        else (Relation.COMPONENT
                              if (multipoint_relation is Relation.COMPONENT
                                  or multipoint_relation is Relation.EQUAL)
                              else Relation.TOUCH))
            elif multisegment_relation is Relation.TOUCH:
                rest_other = other - self.linear
                multipoint_relation = self.multipoint.relate(rest_other)
                return (Relation.COMPONENT
                        if (multipoint_relation is Relation.EQUAL
                            or multipoint_relation is Relation.COMPONENT)
                        else multisegment_relation)
            else:
                return multisegment_relation
        else:
            multipolygon_relation = self.shaped.relate(other)
            if multipolygon_relation in (Relation.COMPONENT,
                                         Relation.ENCLOSED,
                                         Relation.WITHIN):
                return multipolygon_relation
            elif (multipolygon_relation is Relation.TOUCH
                  or multipolygon_relation is Relation.CROSS):
                rest_other = other - self.shaped
                if self.linear is EMPTY:
                    multipoint_relation = self.multipoint.relate(rest_other)
                    return (Relation.COMPONENT
                            if (multipoint_relation is Relation.EQUAL
                                or multipoint_relation is Relation.COMPONENT)
                            else multipolygon_relation)
                else:
                    multisegment_relation = self.linear.relate(rest_other)
                    if multisegment_relation is Relation.DISJOINT:
                        multipoint_relation = self.multipoint.relate(
                                rest_other)
                        return ((Relation.COMPONENT
                                 if multipolygon_relation is Relation.TOUCH
                                 else Relation.ENCLOSED)
                                if (multipoint_relation is Relation.COMPONENT
                                    or multipoint_relation is Relation.EQUAL)
                                else multipolygon_relation)
                    elif multisegment_relation is Relation.TOUCH:
                        rest_other -= self.linear
                        multipoint_relation = self.multipoint.relate(
                                rest_other)
                        return (Relation.COMPONENT
                                if (multipoint_relation is Relation.COMPONENT
                                    or multipoint_relation is Relation.EQUAL)
                                else multipolygon_relation)
                    else:
                        return (Relation.COMPONENT
                                if multipolygon_relation is Relation.TOUCH
                                else Relation.ENCLOSED)
            else:
                multisegment_relation = self.linear.relate(other)
                if multisegment_relation is Relation.DISJOINT:
                    multipoint_relation = self.multipoint.relate(other)
                    return (multipolygon_relation
                            if multipoint_relation is Relation.DISJOINT
                            else (Relation.COMPONENT
                                  if (multipoint_relation is Relation.COMPONENT
                                      or multipoint_relation is Relation.EQUAL)
                                  else Relation.TOUCH))
                elif multisegment_relation is Relation.TOUCH:
                    rest_other = other - self.linear
                    multipoint_relation = self.multipoint.relate(rest_other)
                    return (multipolygon_relation
                            if multipoint_relation is Relation.DISJOINT
                            else (Relation.COMPONENT
                                  if (multipoint_relation is Relation.COMPONENT
                                      or multipoint_relation is Relation.EQUAL)
                                  else Relation.TOUCH))
                else:
                    return multisegment_relation

    def _relate_shaped(self, other: Shaped) -> Relation:
        if self.shaped is EMPTY:
            multisegment_relation = self.linear.relate(other)
            if (multisegment_relation is Relation.DISJOINT
                    or multisegment_relation is Relation.TOUCH):
                multipoint_relation = self.multipoint.relate(other)
                return (multisegment_relation
                        if multipoint_relation is Relation.DISJOINT
                        else (multipoint_relation
                              if (multipoint_relation is Relation.TOUCH
                                  or multipoint_relation is Relation.CROSS)
                              else (Relation.TOUCH
                                    if (multipoint_relation
                                        is Relation.COMPOSITE)
                                    else Relation.CROSS)))
            elif (multisegment_relation is Relation.COVER
                  or multisegment_relation is Relation.ENCLOSES):
                multipoint_relation = self.multipoint.relate(other)
                return (Relation.CROSS
                        if (multipoint_relation is Relation.DISJOINT
                            or multipoint_relation is Relation.TOUCH)
                        else (multipoint_relation
                              if (multipoint_relation is multisegment_relation
                                  or multipoint_relation is Relation.CROSS)
                              else Relation.ENCLOSES))
            elif multisegment_relation is Relation.COMPOSITE:
                multipoint_relation = self.multipoint.relate(other)
                return (Relation.TOUCH
                        if multipoint_relation is Relation.DISJOINT
                        else (multipoint_relation
                              if (multipoint_relation is Relation.TOUCH
                                  or multipoint_relation is Relation.CROSS)
                              else (multisegment_relation
                                    if (multipoint_relation
                                        is multisegment_relation)
                                    else Relation.CROSS)))
            else:
                return multisegment_relation
        else:
            multipolygon_relation = self.shaped.relate(other)
            if multipolygon_relation is Relation.DISJOINT:
                multisegment_relation = self.linear.relate(other)
                if multisegment_relation is Relation.DISJOINT:
                    multipoint_relation = self.multipoint.relate(other)
                    return (multipoint_relation
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                            else (Relation.TOUCH
                                  if multipoint_relation is Relation.COMPOSITE
                                  else Relation.CROSS))
                elif (multisegment_relation is Relation.TOUCH
                      or multisegment_relation is Relation.COMPOSITE):
                    multipoint_relation = self.multipoint.relate(other)
                    return (Relation.TOUCH
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.COMPOSITE)
                            else Relation.CROSS)
                else:
                    return Relation.CROSS
            elif multipolygon_relation is Relation.TOUCH:
                multisegment_relation = self.linear.relate(other)
                if multisegment_relation in (Relation.DISJOINT,
                                             Relation.TOUCH,
                                             Relation.COMPOSITE):
                    multipoint_relation = self.multipoint.relate(other)
                    return (multipolygon_relation
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.COMPOSITE)
                            else Relation.CROSS)
                else:
                    return Relation.CROSS
            elif (multipolygon_relation is Relation.COVER
                  or multipolygon_relation is Relation.COMPOSITE):
                if self.linear is EMPTY:
                    multipoint_relation = self.multipoint.relate(other)
                    return (Relation.OVERLAP
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                            else (multipolygon_relation
                                  if (multipoint_relation
                                      is multipolygon_relation)
                                  else Relation.ENCLOSES))
                else:
                    multisegment_relation = self.linear.relate(other)
                    if multisegment_relation in (Relation.DISJOINT,
                                                 Relation.TOUCH,
                                                 Relation.CROSS):
                        return Relation.OVERLAP
                    elif self.multipoint is EMPTY:
                        return (multipolygon_relation
                                if (multisegment_relation
                                    is multipolygon_relation)
                                else Relation.ENCLOSES)
                    else:
                        multipoint_relation = self.multipoint.relate(other)
                        return (Relation.OVERLAP
                                if multipoint_relation in (Relation.DISJOINT,
                                                           Relation.TOUCH,
                                                           Relation.CROSS)
                                else (multipolygon_relation
                                      if (multipoint_relation
                                          is multisegment_relation
                                          is multipolygon_relation)
                                      else Relation.ENCLOSES))
            elif multipolygon_relation is Relation.ENCLOSES:
                if self.linear is EMPTY:
                    multipoint_relation = self.multipoint.relate(other)
                    return (Relation.OVERLAP
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                            else Relation.ENCLOSES)
                else:
                    multisegment_relation = self.linear.relate(other)
                    if multisegment_relation in (Relation.DISJOINT,
                                                 Relation.TOUCH,
                                                 Relation.CROSS):
                        return Relation.OVERLAP
                    elif self.multipoint is EMPTY:
                        return multipolygon_relation
                    else:
                        multipoint_relation = self.multipoint.relate(other)
                        return (Relation.OVERLAP
                                if multipoint_relation in (Relation.DISJOINT,
                                                           Relation.TOUCH,
                                                           Relation.CROSS)
                                else Relation.ENCLOSES)
            else:
                return (Relation.COMPONENT
                        if multipolygon_relation is Relation.EQUAL
                        else multipolygon_relation)


def from_mix_components(multipoint: Maybe[Multipoint],
                        linear: Maybe[Linear],
                        shaped: Maybe[Shaped]) -> Compound:
    return (Mix(multipoint, linear, shaped)
            if (((multipoint is not EMPTY)
                 + (linear is not EMPTY)
                 + (shaped is not EMPTY))
                >= MIN_MIX_NON_EMPTY_COMPONENTS)
            else (multipoint
                  if multipoint is not EMPTY
                  else (linear
                        if linear is not EMPTY
                        else shaped)))
