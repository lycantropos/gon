from typing import Optional

from ground.hints import (Maybe,
                          Scalar)
from reprit.base import generate_repr

from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation,
                       Shaped)
from .contracts import MIN_MIX_NON_EMPTY_COMPONENTS
from .geometry import (Coordinate,
                       Geometry)
from .iterable import non_negative_min
from .multipoint import Multipoint
from .packing import pack_mix
from .point import Point


class Mix(Indexable[Coordinate]):
    __slots__ = '_components', '_discrete', '_linear', '_shaped'

    def __init__(self,
                 discrete: Maybe[Multipoint[Coordinate]],
                 linear: Maybe[Linear[Coordinate]],
                 shaped: Maybe[Shaped[Coordinate]]) -> None:
        """
        Initializes mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._components = self._discrete, self._linear, self._shaped = (
            discrete, linear, shaped)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns intersection of the mix with the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix & mix == mix
        True
        """
        discrete_part = self.discrete & other
        linear_part = self.linear & other
        shaped_part = self.shaped & other
        context = self._context
        if isinstance(linear_part, Multipoint):
            shaped_part |= linear_part
            linear_part = context.empty
        elif isinstance(linear_part, Mix):
            shaped_part |= linear_part.discrete
            linear_part = linear_part.linear
        if isinstance(shaped_part, Multipoint):
            linear_part |= shaped_part
            if isinstance(linear_part, Mix):
                discrete_part |= linear_part.discrete
                linear_part = linear_part.linear
            shaped_part = context.empty
        elif isinstance(shaped_part, Linear):
            linear_part |= shaped_part
            shaped_part = context.empty
        elif isinstance(shaped_part, Mix):
            linear_part = (linear_part | shaped_part.linear
                           | shaped_part.discrete)
            shaped_part = shaped_part.shaped
        if isinstance(linear_part, Multipoint):
            discrete_part |= linear_part
            linear_part = context.empty
        elif isinstance(linear_part, Mix):
            discrete_part |= linear_part.discrete
            linear_part = linear_part.linear
        return pack_mix(discrete_part, linear_part, shaped_part, context.empty,
                        context.mix_cls)

    __rand__ = __and__

    def __contains__(self, point: Point[Coordinate]) -> bool:
        """
        Checks if the mix contains the point.

        Time complexity:
            ``O(log elements_count)`` expected after indexing,
            ``O(elements_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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

    def __eq__(self, other: 'Mix[Coordinate]') -> bool:
        """
        Checks if mixes are equal.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix == mix
        True
        """
        return self is other or (self._components == other._components
                                 if isinstance(other, Mix)
                                 else NotImplemented)

    def __ge__(self, other: Compound[Coordinate]) -> bool:
        """
        Checks if the mix is a superset of the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix >= mix
        True
        """
        return (other is self._context.empty
                or self == other
                or ((self.shaped is not self._context.empty
                     or not isinstance(other, Shaped)
                     and (not isinstance(other, Mix)
                          or other.shaped is self._context.empty))
                    and self.relate(other) in (Relation.EQUAL,
                                               Relation.COMPONENT,
                                               Relation.ENCLOSED,
                                               Relation.WITHIN)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound[Coordinate]) -> bool:
        """
        Checks if the mix is a strict superset of the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix > mix
        False
        """
        return (other is self._context.empty
                or self != other
                and ((self.shaped is not self._context.empty
                      or not isinstance(other, Shaped)
                      and (not isinstance(other, Mix)
                           or other.shaped is self._context.empty))
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

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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

    def __le__(self, other: Compound[Coordinate]) -> bool:
        """
        Checks if the mix is a subset of the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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
                    and (self.shaped is self._context.empty
                         or not isinstance(other, Linear)
                         and (not isinstance(other, Mix)
                              or other.shaped is not self._context.empty))
                    and self.relate(other) in (Relation.COVER,
                                               Relation.ENCLOSES,
                                               Relation.COMPOSITE,
                                               Relation.EQUAL)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __lt__(self, other: Compound[Coordinate]) -> bool:
        """
        Checks if the mix is a strict subset of the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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
                     and (self.shaped is self._context.empty
                          or not isinstance(other, Linear)
                          and (not isinstance(other, Mix)
                               or other.shaped is not self._context.empty))
                     and self.relate(other) in (Relation.COVER,
                                                Relation.ENCLOSES,
                                                Relation.COMPOSITE)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __or__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns union of the mix with the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix | mix == mix
        True
        """
        context = self._context
        if isinstance(other, Multipoint):
            return context.mix_cls(self.discrete
                                   | (other - self.shaped - self.linear),
                                   self.linear, self.shaped)
        elif isinstance(other, Linear):
            discrete_part, linear_part = self.discrete, self.linear
            shaped_part = self.shaped | other
            if isinstance(shaped_part, Linear):
                linear_part = linear_part | shaped_part | discrete_part
                shaped_part = context.empty
            elif isinstance(shaped_part, Mix):
                linear_part = linear_part | shaped_part.linear | discrete_part
                shaped_part = shaped_part.shaped
            else:
                # other is subset of the shaped component
                return pack_mix(discrete_part, linear_part, shaped_part,
                                context.empty, context.mix_cls)
            if isinstance(linear_part, Mix):
                discrete_part, linear_part = (linear_part.discrete,
                                              linear_part.linear)
            else:
                discrete_part = context.empty
            return pack_mix(discrete_part, linear_part, shaped_part,
                            context.empty, context.mix_cls)
        elif isinstance(other, (Shaped, Mix)):
            return self.shaped | other | self.linear | self.discrete
        else:
            return NotImplemented

    __ror__ = __or__

    def __rsub__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns difference of the other geometry with the mix.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))
        """
        return ((other - self.discrete) & (other - self.linear)
                & other - self.shaped)

    def __sub__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns difference of the mix with the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (EMPTY, Contour, Mix, Multipoint, Point,
        ...                       Polygon, Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix - mix is EMPTY
        True
        """
        return pack_mix(self.discrete - other, self.linear - other,
                        self.shaped - other, self._context.empty,
                        self._context.mix_cls)

    def __xor__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns symmetric difference of the mix with the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (EMPTY, Contour, Mix, Multipoint, Point,
        ...                       Polygon, Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix ^ mix is EMPTY
        True
        """
        context = self._context
        if isinstance(other, Multipoint):
            rest_other = other - self.shaped - self.linear
            return pack_mix(self.discrete ^ rest_other, self.linear,
                            self.shaped, context.empty, context.mix_cls)
        elif isinstance(other, Linear):
            discrete_part, linear_part = self.discrete, self.linear
            shaped_part = self.shaped ^ other
            if isinstance(shaped_part, Linear):
                linear_part = linear_part ^ shaped_part ^ discrete_part
                shaped_part = context.empty
            elif isinstance(shaped_part, Mix):
                linear_part = linear_part ^ shaped_part.linear ^ discrete_part
                shaped_part = shaped_part.shaped
            else:
                # other is subset of the shaped component
                return pack_mix(discrete_part, linear_part, shaped_part,
                                context.empty, context.mix_cls)
            if isinstance(linear_part, Mix):
                discrete_part, linear_part = (linear_part.discrete,
                                              linear_part.linear)
            else:
                discrete_part = context.empty
            return pack_mix(discrete_part, linear_part, shaped_part,
                            context.empty, context.mix_cls)
        elif isinstance(other, (Shaped, Mix)):
            return self.shaped ^ other ^ self.linear ^ self.discrete
        else:
            return NotImplemented

    __rxor__ = __xor__

    @property
    def centroid(self) -> Point[Coordinate]:
        """
        Returns centroid of the mix.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.centroid == Point(3, 3)
        True
        """
        return (self.linear
                if self.shaped is self._context.empty
                else self.shaped).centroid

    @property
    def discrete(self) -> Maybe[Multipoint[Coordinate]]:
        """
        Returns disrete component of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.discrete == Multipoint([Point(3, 3)])
        True
        """
        return self._discrete

    @property
    def shaped(self) -> Maybe[Shaped[Coordinate]]:
        """
        Returns shaped component of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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
    def linear(self) -> Maybe[Linear[Coordinate]]:
        """
        Returns linear component of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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

    def distance_to(self, other: Geometry[Coordinate]) -> Scalar:
        """
        Returns distance between the mix and the other geometry.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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
                                if component is not self._context.empty)

    def index(self) -> None:
        """
        Pre-processes the mix to potentially improve queries.

        Time complexity:
            ``O(elements_count * log elements_count)`` expected,
            ``O(elements_count ** 2)`` worst
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.index()
        """
        if isinstance(self.discrete, Indexable):
            self.discrete.index()
        if isinstance(self.linear, Indexable):
            self.linear.index()
        if isinstance(self.shaped, Indexable):
            self.shaped.index()

    def locate(self, point: Point[Coordinate]) -> Location:
        """
        Finds location of the point relative to the mix.

        Time complexity:
            ``O(log elements_count)`` expected after indexing,
            ``O(elements_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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

    def relate(self, other: Compound[Coordinate]) -> Relation:
        """
        Finds relation between the mix and the other geometry.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.relate(mix) is Relation.EQUAL
        True
        """
        return (self._relate_discrete(other)
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
               point: Optional[Point[Coordinate]] = None) -> 'Mix[Coordinate]':
        """
        Rotates the mix by given cosine & sine around given point.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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
        return self._context.mix_cls(self.discrete.rotate(cosine, sine, point),
                                     self.linear.rotate(cosine, sine, point),
                                     self.shaped.rotate(cosine, sine, point))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> Compound[Coordinate]:
        """
        Scales the mix by given factor.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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
        return (self._context.mix_cls(self.discrete.scale(factor_x, factor_y),
                                      self.linear.scale(factor_x, factor_y),
                                      self.shaped.scale(factor_x, factor_y))
                if factor_x and factor_y
                else ((self.discrete.scale(factor_x, factor_y)
                       | self.linear.scale(factor_x, factor_y)
                       | self.shaped.scale(factor_x, factor_y))
                      if factor_x or factor_y
                      else
                      self._context.multipoint_cls(
                              [self._context.point_cls(factor_x, factor_y)])))

    def translate(self,
                  step_x: Coordinate,
                  step_y: Coordinate) -> 'Mix[Coordinate]':
        """
        Translates the mix by given step.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
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
        return self._context.mix_cls(self.discrete.translate(step_x, step_y),
                                     self.linear.translate(step_x, step_y),
                                     self.shaped.translate(step_x, step_y))

    def validate(self) -> None:
        """
        Checks if the mix is valid.

        Time complexity:
            ``O(elements_count * log elements_count)``
        Memory complexity:
            ``O(elements_count)``

        where

            .. code-block:: python

                elements_count = discrete_size + linear_size\
 + shaped_vertices_count
                discrete_size = len(points)
                linear_size = len(segments)
                shaped_vertices_count = (sum(len(polygon.border.vertices)
                                         + sum(len(hole.vertices)
                                               for hole in polygon.holes)
                                         for polygon in polygons)
                points = [] if self.discrete is EMPTY else self.discrete.points
                segments = ([]
                            if self.linear is EMPTY
                            else ([self.linear]
                                  if isinstance(self.linear, Segment)
                                  else self.linear.segments))
                polygons = ([]
                            if self.shaped is EMPTY
                            else (self.shaped.polygons
                                  if isinstance(self.linear, Multipolygon)
                                  else [self.shaped]))

        >>> from gon.base import (Contour, Mix, Multipoint, Point, Polygon,
        ...                       Segment)
        >>> mix = Mix(Multipoint([Point(3, 3)]),
        ...           Segment(Point(6, 6), Point(6, 8)),
        ...           Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])]))
        >>> mix.validate()
        """
        if (sum(component is not self._context.empty for component in
                self._components)
                < MIN_MIX_NON_EMPTY_COMPONENTS):
            raise ValueError('At least {count} components should not be empty.'
                             .format(count=MIN_MIX_NON_EMPTY_COMPONENTS))
        for component in self._components:
            component.validate()
        if (not self.discrete.disjoint(self.linear)
                or not self.discrete.disjoint(self.shaped)):
            raise ValueError('Discrete component should be disjoint '
                             'from other components.')
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
                      in (Relation.OVERLAP, Relation.COMPOSITE)
                      or any(hole.relate(self.linear)
                             in (Relation.OVERLAP, Relation.COMPOSITE)
                             for hole in polygon.holes)
                      for polygon in (
                              self.shaped.polygons
                              if isinstance(self.shaped,
                                            self._context.multipolygon_cls)
                              else [self.shaped]))):
            raise ValueError('Linear component should not overlap '
                             'shaped component borders.')

    def _relate_linear(self, other: Linear[Coordinate]) -> Relation:
        if self.shaped is self._context.empty:
            linear_relation = self.linear.relate(other)
            if linear_relation is Relation.DISJOINT:
                discrete_relation = self.discrete.relate(other)
                return (Relation.TOUCH
                        if discrete_relation is Relation.COMPOSITE
                        else discrete_relation)
            elif linear_relation is Relation.COMPOSITE:
                discrete_relation = self.discrete.relate(other)
                return (linear_relation
                        if discrete_relation is linear_relation
                        else Relation.OVERLAP)
            else:
                return (Relation.COMPONENT
                        if linear_relation is Relation.EQUAL
                        else linear_relation)
        else:
            shaped_relation = self.shaped.relate(other)
            if shaped_relation is Relation.DISJOINT:
                linear_relation = self.linear.relate(other)
                if linear_relation is Relation.DISJOINT:
                    discrete_relation = self.discrete.relate(other)
                    return (Relation.TOUCH
                            if discrete_relation is Relation.COMPOSITE
                            else discrete_relation)
                elif linear_relation in (Relation.TOUCH,
                                         Relation.CROSS,
                                         Relation.COMPONENT):
                    return linear_relation
                else:
                    return (Relation.COMPONENT
                            if linear_relation is Relation.EQUAL
                            else Relation.TOUCH)
            elif (shaped_relation is Relation.TOUCH
                  or shaped_relation is Relation.CROSS):
                rest_other = other - self.shaped
                linear_relation = self.linear.relate(rest_other)
                return (Relation.COMPONENT
                        if (linear_relation is Relation.EQUAL
                            or linear_relation is Relation.COMPONENT)
                        else shaped_relation)
            else:
                return shaped_relation

    def _relate_mix(self, other: 'Mix[Coordinate]') -> Relation:
        if self.shaped is other.shaped is self._context.empty:
            linear_components_relation = self.linear.relate(other.linear)
            if linear_components_relation is Relation.DISJOINT:
                return (linear_components_relation
                        if (self._relate_discrete(other.discrete)
                            is other._relate_discrete(self.discrete)
                            is linear_components_relation)
                        else Relation.TOUCH)
            elif linear_components_relation is Relation.COMPOSITE:
                discrete_relation = other._relate_discrete(self.discrete)
                return (linear_components_relation
                        if discrete_relation is Relation.COMPONENT
                        else Relation.OVERLAP)
            elif linear_components_relation is Relation.EQUAL:
                other_discrete_relation = self.discrete.relate(other.discrete)
                return (Relation.OVERLAP
                        if other_discrete_relation is Relation.DISJOINT
                        else other_discrete_relation)
            elif linear_components_relation is Relation.COMPONENT:
                other_discrete_relation = self._relate_discrete(other.discrete)
                return (linear_components_relation
                        if other_discrete_relation is Relation.COMPONENT
                        else Relation.OVERLAP)
            else:
                return linear_components_relation
        elif self.shaped is self._context.empty:
            linear_relation = other._relate_linear(self.linear)
            if linear_relation is Relation.CROSS:
                return linear_relation
            discrete_relation = other._relate_discrete(self.discrete)
            if linear_relation is Relation.DISJOINT:
                return (discrete_relation
                        if discrete_relation in (Relation.DISJOINT,
                                                 Relation.TOUCH,
                                                 Relation.CROSS)
                        else (Relation.TOUCH
                              if discrete_relation is Relation.COMPONENT
                              else Relation.CROSS))
            elif linear_relation is Relation.TOUCH:
                return (Relation.CROSS
                        if discrete_relation in (Relation.CROSS,
                                                 Relation.ENCLOSED,
                                                 Relation.WITHIN)
                        else linear_relation)
            elif linear_relation is Relation.COMPONENT:
                return (Relation.TOUCH
                        if discrete_relation is Relation.DISJOINT
                        else (discrete_relation
                              if (discrete_relation is Relation.TOUCH
                                  or discrete_relation is Relation.CROSS)
                              else (Relation.COMPOSITE
                                    if discrete_relation is Relation.COMPONENT
                                    else Relation.ENCLOSES)))
            else:
                return (Relation.CROSS
                        if discrete_relation in (Relation.DISJOINT,
                                                 Relation.TOUCH,
                                                 Relation.CROSS)
                        else (Relation.COVER
                              if discrete_relation is Relation.WITHIN
                              else Relation.ENCLOSES))
        elif other.shaped is self._context.empty:
            other_linear_relation = self._relate_linear(other.linear)
            if other_linear_relation is Relation.CROSS:
                return other_linear_relation
            other_discrete_relation = self._relate_discrete(other.discrete)
            if other_linear_relation is Relation.DISJOINT:
                return (other_discrete_relation
                        if other_discrete_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                        else (Relation.TOUCH
                              if other_discrete_relation is Relation.COMPONENT
                              else Relation.CROSS))
            elif other_linear_relation is Relation.TOUCH:
                return (Relation.CROSS
                        if other_discrete_relation in (Relation.CROSS,
                                                       Relation.ENCLOSED,
                                                       Relation.WITHIN)
                        else other_linear_relation)
            elif other_linear_relation is Relation.COMPONENT:
                return (Relation.TOUCH
                        if (other_discrete_relation is Relation.DISJOINT
                            or other_discrete_relation is Relation.TOUCH)
                        else (other_discrete_relation
                              if (other_discrete_relation is Relation.CROSS
                                  or (other_discrete_relation
                                      is Relation.COMPONENT))
                              else Relation.ENCLOSED))
            elif other_linear_relation is Relation.ENCLOSED:
                return (Relation.CROSS
                        if other_discrete_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                        else other_linear_relation)
            else:
                return (Relation.CROSS
                        if other_discrete_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                        else (Relation.ENCLOSED
                              if other_discrete_relation is Relation.COMPONENT
                              else other_linear_relation))
        shaped_components_relation = self.shaped.relate(other.shaped)
        if (shaped_components_relation is Relation.DISJOINT
                or shaped_components_relation is Relation.TOUCH):
            if self.linear is other.linear is self._context.empty:
                other_discrete_relation = self._relate_discrete(other.discrete)
                if other_discrete_relation is Relation.CROSS:
                    return other_discrete_relation
                elif (other_discrete_relation is Relation.ENCLOSED
                      or other_discrete_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    discrete_relation = other._relate_discrete(self.discrete)
                    if (discrete_relation
                            is other_discrete_relation
                            is Relation.DISJOINT):
                        return shaped_components_relation
                    elif discrete_relation is Relation.CROSS:
                        return discrete_relation
                    elif (discrete_relation is Relation.ENCLOSED
                          or discrete_relation is Relation.WITHIN):
                        return Relation.CROSS
                    else:
                        return Relation.TOUCH
            elif self.linear is self._context.empty:
                other_linear_relation = self._relate_linear(other.linear)
                if other_linear_relation is Relation.CROSS:
                    return other_linear_relation
                elif (other_linear_relation is Relation.ENCLOSED
                      or other_linear_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    discrete_relation = other._relate_discrete(self.discrete)
                    if discrete_relation is Relation.CROSS:
                        return discrete_relation
                    elif (discrete_relation is Relation.ENCLOSED
                          or discrete_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif other.discrete is self._context.empty:
                        return (shaped_components_relation
                                if (discrete_relation
                                    is other_linear_relation
                                    is Relation.DISJOINT)
                                else Relation.TOUCH)
                    else:
                        other_discrete_relation = self._relate_discrete(
                                other.discrete)
                        if other_discrete_relation is Relation.CROSS:
                            return other_discrete_relation
                        elif (other_discrete_relation is Relation.ENCLOSED
                              or other_discrete_relation is Relation.WITHIN):
                            return Relation.CROSS
                        elif (discrete_relation
                              is other_discrete_relation
                              is other_linear_relation
                              is Relation.DISJOINT):
                            return shaped_components_relation
                        else:
                            return Relation.TOUCH
            elif other.linear is self._context.empty:
                linear_relation = other._relate_linear(self.linear)
                if linear_relation is Relation.CROSS:
                    return linear_relation
                elif (linear_relation is Relation.ENCLOSED
                      or linear_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    other_discrete_relation = self._relate_discrete(
                            other.discrete)
                    if other_discrete_relation is Relation.CROSS:
                        return other_discrete_relation
                    elif (other_discrete_relation is Relation.ENCLOSED
                          or other_discrete_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif self.discrete is self._context.empty:
                        return (shaped_components_relation
                                if (linear_relation
                                    is other_discrete_relation
                                    is Relation.DISJOINT)
                                else Relation.TOUCH)
                    else:
                        discrete_relation = other._relate_discrete(
                                self.discrete)
                        if discrete_relation is Relation.CROSS:
                            return discrete_relation
                        elif (discrete_relation is Relation.ENCLOSED
                              or discrete_relation is Relation.WITHIN):
                            return Relation.CROSS
                        elif (discrete_relation
                              is linear_relation
                              is other_discrete_relation
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
                    elif self.discrete is self._context.empty:
                        other_discrete_relation = self._relate_discrete(
                                other.discrete)
                        return (other_discrete_relation
                                if other_discrete_relation is Relation.CROSS
                                else
                                (Relation.CROSS
                                 if (other_discrete_relation
                                     is Relation.ENCLOSED
                                     or other_discrete_relation
                                     is Relation.WITHIN)
                                 else (shaped_components_relation
                                       if (other_discrete_relation
                                           is linear_relation
                                           is other_linear_relation
                                           is Relation.DISJOINT)
                                       else Relation.TOUCH)))
                    elif other.discrete is self._context.empty:
                        discrete_relation = other._relate_discrete(
                                self.discrete)
                        return (discrete_relation
                                if discrete_relation is Relation.CROSS
                                else
                                (Relation.CROSS
                                 if (discrete_relation is Relation.ENCLOSED
                                     or discrete_relation is Relation.WITHIN)
                                 else (shaped_components_relation
                                       if (discrete_relation
                                           is linear_relation
                                           is other_linear_relation
                                           is Relation.DISJOINT)
                                       else Relation.TOUCH)))
                    else:
                        other_discrete_relation = self._relate_discrete(
                                other.discrete)
                        if other_discrete_relation is Relation.CROSS:
                            return other_discrete_relation
                        elif (other_discrete_relation is Relation.ENCLOSED
                              or other_discrete_relation is Relation.WITHIN):
                            return Relation.CROSS
                        else:
                            discrete_relation = other._relate_discrete(
                                    self.discrete)
                            return (discrete_relation
                                    if discrete_relation is Relation.CROSS
                                    else (Relation.CROSS
                                          if (discrete_relation
                                              is Relation.ENCLOSED
                                              or discrete_relation
                                              is Relation.WITHIN)
                                          else
                                          (shaped_components_relation
                                           if (discrete_relation
                                               is linear_relation
                                               is other_discrete_relation
                                               is other_linear_relation
                                               is Relation.DISJOINT)
                                           else Relation.TOUCH)))
        elif shaped_components_relation in (Relation.COVER,
                                            Relation.ENCLOSES,
                                            Relation.COMPOSITE):
            if self.linear is self._context.empty:
                discrete_relation = (other._relate_discrete(self.discrete)
                                     .complement)
                return (shaped_components_relation
                        if discrete_relation is shaped_components_relation
                        else (Relation.ENCLOSES
                              if discrete_relation in (Relation.COVER,
                                                       Relation.ENCLOSES,
                                                       Relation.COMPOSITE)
                              else Relation.OVERLAP))
            else:
                linear_relation = other._relate_linear(self.linear).complement
                if linear_relation is shaped_components_relation:
                    if self.discrete is self._context.empty:
                        return shaped_components_relation
                    else:
                        discrete_relation = other._relate_discrete(
                                self.discrete).complement
                        return (shaped_components_relation
                                if (discrete_relation
                                    is shaped_components_relation)
                                else
                                (Relation.ENCLOSES
                                 if discrete_relation in (Relation.COVER,
                                                          Relation.ENCLOSES,
                                                          Relation.COMPOSITE)
                                 else Relation.OVERLAP))
                elif linear_relation in (Relation.COVER,
                                         Relation.ENCLOSES,
                                         Relation.COMPOSITE):
                    if self.discrete is self._context.empty:
                        return Relation.ENCLOSES
                    else:
                        discrete_relation = other._relate_discrete(
                                self.discrete).complement
                        return (Relation.ENCLOSES
                                if discrete_relation in (Relation.COVER,
                                                         Relation.ENCLOSES,
                                                         Relation.COMPOSITE)
                                else Relation.OVERLAP)
                else:
                    return Relation.OVERLAP
        elif shaped_components_relation is Relation.EQUAL:
            linear_components_relation = self.linear.relate(other.linear)
            if self.linear is other.linear is self._context.empty:
                discrete_components_relation = self.discrete.relate(
                        other.discrete)
                return (
                    shaped_components_relation
                    if (self.discrete is other.discrete is self._context.empty
                        or discrete_components_relation is Relation.EQUAL)
                    else
                    (discrete_components_relation
                     if (discrete_components_relation is Relation.COMPOSITE
                         or discrete_components_relation is Relation.COMPONENT)
                     else Relation.OVERLAP))
            elif self.linear is self._context.empty:
                discrete_components_relation = other._relate_discrete(
                        self.discrete)
                return (
                    Relation.COMPOSITE
                    if (discrete_components_relation is Relation.EQUAL
                        or discrete_components_relation is Relation.COMPONENT)
                    else Relation.OVERLAP)
            elif other.linear is self._context.empty:
                discrete_components_relation = self._relate_discrete(
                        other.discrete)
                return (
                    Relation.COMPONENT
                    if (discrete_components_relation is Relation.EQUAL
                        or discrete_components_relation is Relation.COMPONENT)
                    else Relation.OVERLAP)
            elif linear_components_relation is Relation.COMPOSITE:
                discrete_components_relation = other._relate_discrete(
                        self.discrete)
                return (
                    linear_components_relation
                    if (self.discrete is self._context.empty
                        or discrete_components_relation is Relation.EQUAL
                        or discrete_components_relation is Relation.COMPONENT)
                    else Relation.OVERLAP)
            elif linear_components_relation is Relation.EQUAL:
                discrete_components_relation = self.discrete.relate(
                        other.discrete)
                return (
                    shaped_components_relation
                    if (self.discrete is other.discrete is self._context.empty
                        or discrete_components_relation is Relation.EQUAL)
                    else
                    (Relation.COMPOSITE
                     if self.discrete is self._context.empty
                     else
                     (Relation.COMPONENT
                      if other.discrete is self._context.empty
                      else
                      (discrete_components_relation
                       if
                       (discrete_components_relation is Relation.COMPONENT
                        or discrete_components_relation is Relation.COMPOSITE)
                       else Relation.OVERLAP))))
            elif linear_components_relation is Relation.COMPONENT:
                discrete_components_relation = self._relate_discrete(
                        other.discrete)
                return (
                    linear_components_relation
                    if (other.discrete is self._context.empty
                        or discrete_components_relation is Relation.EQUAL
                        or discrete_components_relation is Relation.COMPONENT)
                    else Relation.OVERLAP)
            else:
                return Relation.OVERLAP
        elif shaped_components_relation in (Relation.COMPONENT,
                                            Relation.ENCLOSED,
                                            Relation.WITHIN):
            if other.linear is self._context.empty:
                discrete_relation = self._relate_discrete(other.discrete)
                return (shaped_components_relation
                        if discrete_relation is shaped_components_relation
                        else (Relation.ENCLOSED
                              if discrete_relation in (Relation.COMPONENT,
                                                       Relation.ENCLOSED,
                                                       Relation.WITHIN)
                              else Relation.OVERLAP))
            else:
                linear_relation = self._relate_linear(other.linear)
                if linear_relation is shaped_components_relation:
                    if other.discrete is self._context.empty:
                        return shaped_components_relation
                    else:
                        discrete_relation = self._relate_discrete(
                                other.discrete)
                        return (shaped_components_relation
                                if (discrete_relation
                                    is shaped_components_relation)
                                else
                                (Relation.ENCLOSED
                                 if discrete_relation in (Relation.COMPONENT,
                                                          Relation.ENCLOSED,
                                                          Relation.WITHIN)
                                 else Relation.OVERLAP))
                elif linear_relation in (Relation.COMPONENT,
                                         Relation.ENCLOSED,
                                         Relation.WITHIN):
                    if other.discrete is self._context.empty:
                        return Relation.ENCLOSED
                    else:
                        discrete_relation = self._relate_discrete(
                                other.discrete)
                        return (Relation.ENCLOSED
                                if discrete_relation in (Relation.COMPONENT,
                                                         Relation.ENCLOSED,
                                                         Relation.WITHIN)
                                else Relation.OVERLAP)
                else:
                    return Relation.OVERLAP
        else:
            return shaped_components_relation

    def _relate_discrete(self, other: Multipoint[Coordinate]) -> Relation:
        if self.shaped is self._context.empty:
            linear_relation = self.linear.relate(other)
            if linear_relation is Relation.DISJOINT:
                discrete_relation = self.discrete.relate(other)
                return (discrete_relation
                        if discrete_relation is Relation.DISJOINT
                        else (Relation.COMPONENT
                              if (discrete_relation is Relation.COMPONENT
                                  or discrete_relation is Relation.EQUAL)
                              else Relation.TOUCH))
            elif linear_relation is Relation.TOUCH:
                rest_other = other - self.linear
                discrete_relation = self.discrete.relate(rest_other)
                return (Relation.COMPONENT
                        if (discrete_relation is Relation.EQUAL
                            or discrete_relation is Relation.COMPONENT)
                        else linear_relation)
            else:
                return linear_relation
        else:
            shaped_relation = self.shaped.relate(other)
            if shaped_relation in (Relation.COMPONENT,
                                   Relation.ENCLOSED,
                                   Relation.WITHIN):
                return shaped_relation
            elif (shaped_relation is Relation.TOUCH
                  or shaped_relation is Relation.CROSS):
                rest_other = other - self.shaped
                if self.linear is self._context.empty:
                    discrete_relation = self.discrete.relate(rest_other)
                    return (Relation.COMPONENT
                            if (discrete_relation is Relation.EQUAL
                                or discrete_relation is Relation.COMPONENT)
                            else shaped_relation)
                else:
                    linear_relation = self.linear.relate(rest_other)
                    if linear_relation is Relation.DISJOINT:
                        discrete_relation = self.discrete.relate(rest_other)
                        return ((Relation.COMPONENT
                                 if shaped_relation is Relation.TOUCH
                                 else Relation.ENCLOSED)
                                if (discrete_relation is Relation.COMPONENT
                                    or discrete_relation is Relation.EQUAL)
                                else shaped_relation)
                    elif linear_relation is Relation.TOUCH:
                        rest_other -= self.linear
                        discrete_relation = self.discrete.relate(rest_other)
                        return (Relation.COMPONENT
                                if (discrete_relation is Relation.COMPONENT
                                    or discrete_relation is Relation.EQUAL)
                                else shaped_relation)
                    else:
                        return (Relation.COMPONENT
                                if shaped_relation is Relation.TOUCH
                                else Relation.ENCLOSED)
            else:
                linear_relation = self.linear.relate(other)
                if linear_relation is Relation.DISJOINT:
                    discrete_relation = self.discrete.relate(other)
                    return (shaped_relation
                            if discrete_relation is Relation.DISJOINT
                            else (Relation.COMPONENT
                                  if (discrete_relation is Relation.COMPONENT
                                      or discrete_relation is Relation.EQUAL)
                                  else Relation.TOUCH))
                elif linear_relation is Relation.TOUCH:
                    rest_other = other - self.linear
                    discrete_relation = self.discrete.relate(rest_other)
                    return (shaped_relation
                            if discrete_relation is Relation.DISJOINT
                            else (Relation.COMPONENT
                                  if (discrete_relation is Relation.COMPONENT
                                      or discrete_relation is Relation.EQUAL)
                                  else Relation.TOUCH))
                else:
                    return linear_relation

    def _relate_shaped(self, other: Shaped[Coordinate]) -> Relation:
        if self.shaped is self._context.empty:
            linear_relation = self.linear.relate(other)
            if (linear_relation is Relation.DISJOINT
                    or linear_relation is Relation.TOUCH):
                discrete_relation = self.discrete.relate(other)
                return (linear_relation
                        if discrete_relation is Relation.DISJOINT
                        else (discrete_relation
                              if (discrete_relation is Relation.TOUCH
                                  or discrete_relation is Relation.CROSS)
                              else (Relation.TOUCH
                                    if (discrete_relation
                                        is Relation.COMPOSITE)
                                    else Relation.CROSS)))
            elif (linear_relation is Relation.COVER
                  or linear_relation is Relation.ENCLOSES):
                discrete_relation = self.discrete.relate(other)
                return (Relation.CROSS
                        if (discrete_relation is Relation.DISJOINT
                            or discrete_relation is Relation.TOUCH)
                        else (discrete_relation
                              if (discrete_relation is linear_relation
                                  or discrete_relation is Relation.CROSS)
                              else Relation.ENCLOSES))
            elif linear_relation is Relation.COMPOSITE:
                discrete_relation = self.discrete.relate(other)
                return (Relation.TOUCH
                        if discrete_relation is Relation.DISJOINT
                        else (discrete_relation
                              if (discrete_relation is Relation.TOUCH
                                  or discrete_relation is Relation.CROSS)
                              else (linear_relation
                                    if discrete_relation is linear_relation
                                    else Relation.CROSS)))
            else:
                return linear_relation
        else:
            shaped_relation = self.shaped.relate(other)
            if shaped_relation is Relation.DISJOINT:
                linear_relation = self.linear.relate(other)
                if linear_relation is Relation.DISJOINT:
                    discrete_relation = self.discrete.relate(other)
                    return (discrete_relation
                            if discrete_relation in (Relation.DISJOINT,
                                                     Relation.TOUCH,
                                                     Relation.CROSS)
                            else (Relation.TOUCH
                                  if discrete_relation is Relation.COMPOSITE
                                  else Relation.CROSS))
                elif (linear_relation is Relation.TOUCH
                      or linear_relation is Relation.COMPOSITE):
                    discrete_relation = self.discrete.relate(other)
                    return (Relation.TOUCH
                            if discrete_relation in (Relation.DISJOINT,
                                                     Relation.TOUCH,
                                                     Relation.COMPOSITE)
                            else Relation.CROSS)
                else:
                    return Relation.CROSS
            elif shaped_relation is Relation.TOUCH:
                linear_relation = self.linear.relate(other)
                if linear_relation in (Relation.DISJOINT,
                                       Relation.TOUCH,
                                       Relation.COMPOSITE):
                    discrete_relation = self.discrete.relate(other)
                    return (shaped_relation
                            if discrete_relation in (Relation.DISJOINT,
                                                     Relation.TOUCH,
                                                     Relation.COMPOSITE)
                            else Relation.CROSS)
                else:
                    return Relation.CROSS
            elif (shaped_relation is Relation.COVER
                  or shaped_relation is Relation.COMPOSITE):
                if self.linear is self._context.empty:
                    discrete_relation = self.discrete.relate(other)
                    return (Relation.OVERLAP
                            if discrete_relation in (Relation.DISJOINT,
                                                     Relation.TOUCH,
                                                     Relation.CROSS)
                            else (shaped_relation
                                  if discrete_relation is shaped_relation
                                  else Relation.ENCLOSES))
                else:
                    linear_relation = self.linear.relate(other)
                    if linear_relation in (Relation.DISJOINT,
                                           Relation.TOUCH,
                                           Relation.CROSS):
                        return Relation.OVERLAP
                    elif self.discrete is self._context.empty:
                        return (shaped_relation
                                if linear_relation is shaped_relation
                                else Relation.ENCLOSES)
                    else:
                        discrete_relation = self.discrete.relate(other)
                        return (Relation.OVERLAP
                                if discrete_relation in (Relation.DISJOINT,
                                                         Relation.TOUCH,
                                                         Relation.CROSS)
                                else (shaped_relation
                                      if (discrete_relation
                                          is linear_relation
                                          is shaped_relation)
                                      else Relation.ENCLOSES))
            elif shaped_relation is Relation.ENCLOSES:
                if self.linear is self._context.empty:
                    discrete_relation = self.discrete.relate(other)
                    return (Relation.OVERLAP
                            if discrete_relation in (Relation.DISJOINT,
                                                     Relation.TOUCH,
                                                     Relation.CROSS)
                            else Relation.ENCLOSES)
                else:
                    linear_relation = self.linear.relate(other)
                    if linear_relation in (Relation.DISJOINT,
                                           Relation.TOUCH,
                                           Relation.CROSS):
                        return Relation.OVERLAP
                    elif self.discrete is self._context.empty:
                        return shaped_relation
                    else:
                        discrete_relation = self.discrete.relate(other)
                        return (Relation.OVERLAP
                                if discrete_relation in (Relation.DISJOINT,
                                                         Relation.TOUCH,
                                                         Relation.CROSS)
                                else Relation.ENCLOSES)
            else:
                return (Relation.COMPONENT
                        if shaped_relation is Relation.EQUAL
                        else shaped_relation)
