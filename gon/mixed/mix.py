from typing import Optional

from reprit.base import generate_repr

from gon.compound import (Compound,
                          Indexable,
                          Linear,
                          Location,
                          Relation,
                          Shaped)
from gon.degenerate import (EMPTY,
                            RAW_EMPTY,
                            Maybe)
from gon.discrete import Multipoint
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.linear import (Multisegment,
                        Segment)
from gon.mixed import RawMix
from gon.primitive import Point
from gon.shaped import (Multipolygon,
                        Polygon)

MIN_MIX_NON_EMPTY_COMPONENTS = 2


class Mix(Indexable):
    __slots__ = '_multipoint', '_multisegment', '_multipolygon', '_components'

    def __init__(self, multipoint: Maybe[Multipoint],
                 multisegment: Maybe[Multisegment],
                 multipolygon: Maybe[Multipolygon]) -> None:
        """
        Initializes mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._multipoint = multipoint
        self._multisegment = multisegment
        self._multipolygon = multipolygon
        self._components = (self._multipoint, self._multisegment,
                            self._multipolygon)

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix & mix == mix
        True
        """
        multipoint_part = self._multipoint & other
        multisegment_part = self._multisegment & other
        multipolygon_part = self._multipolygon & other
        if isinstance(multisegment_part, Multipoint):
            multipolygon_part |= multisegment_part
            multisegment_part = EMPTY
        elif isinstance(multisegment_part, Mix):
            multipolygon_part |= multisegment_part._multipoint
            multisegment_part = multisegment_part._multisegment
        if isinstance(multipolygon_part, Multipoint):
            multisegment_part |= multipolygon_part
            if isinstance(multisegment_part, Mix):
                multipoint_part |= multisegment_part._multipoint
                multisegment_part = multisegment_part._multisegment
            multipolygon_part = EMPTY
        elif isinstance(multipolygon_part, Linear):
            multisegment_part |= multipolygon_part
            multipolygon_part = EMPTY
        elif isinstance(multipolygon_part, Mix):
            multisegment_part = (multisegment_part
                                 | multipolygon_part._multisegment
                                 | multipolygon_part._multipoint)
            multipolygon_part = multipolygon_part._multipolygon
        if isinstance(multisegment_part, Multipoint):
            multipoint_part |= multisegment_part
            multisegment_part = EMPTY
        elif isinstance(multisegment_part, Mix):
            multipoint_part |= multisegment_part._multipoint
            multisegment_part = multisegment_part._multisegment
        return from_mix_components(multipoint_part, multisegment_part,
                                   multipolygon_part)

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
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
        return isinstance(other, Point) and bool(self.locate(other))

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix == mix
        True
        """
        return self is other or (self._components == other._components
                                 if isinstance(other, Mix)
                                 else (False
                                       if isinstance(other, Geometry)
                                       else NotImplemented))

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix >= mix
        True
        """
        return (other is EMPTY
                or self == other
                or ((self._multipolygon is not EMPTY
                     or not isinstance(other, Shaped)
                     and (not isinstance(other, Mix)
                          or other._multipolygon is EMPTY))
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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix > mix
        False
        """
        return (other is EMPTY
                or self != other
                and ((self._multipolygon is not EMPTY
                      or not isinstance(other, Shaped)
                      and (not isinstance(other, Mix)
                           or other._multipolygon is EMPTY))
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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix <= mix
        True
        """
        return (self == other
                or (not isinstance(other, Multipoint)
                    and (self._multipolygon is EMPTY
                         or not isinstance(other, Linear)
                         and (not isinstance(other, Mix)
                              or other._multipolygon is not EMPTY))
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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix < mix
        False
        """
        return (self != other
                and (not isinstance(other, Multipoint)
                     and (self._multipolygon is EMPTY
                          or not isinstance(other, Linear)
                          and (not isinstance(other, Mix)
                               or other._multipolygon is not EMPTY))
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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix | mix == mix
        True
        """
        if isinstance(other, Multipoint):
            return Mix(self._multipoint
                       | (other - self._multipolygon - self._multisegment),
                       self._multisegment,
                       self._multipolygon)
        elif isinstance(other, Linear):
            multipoint_part, multisegment_part = (self._multipoint,
                                                  self._multisegment)
            multipolygon_part = self._multipolygon | other
            if isinstance(multipolygon_part, Linear):
                multisegment_part = (multisegment_part | multipolygon_part
                                     | multipoint_part)
                multipolygon_part = EMPTY
            elif isinstance(multipolygon_part, Mix):
                multisegment_part = (multisegment_part
                                     | multipolygon_part._multisegment
                                     | multipoint_part)
                multipolygon_part = multipolygon_part._multipolygon
            else:
                # other is subset of the multipolygon
                return from_mix_components(multipoint_part, multisegment_part,
                                           multipolygon_part)
            if isinstance(multisegment_part, Mix):
                multipoint_part, multisegment_part = (
                    multisegment_part._multipoint,
                    multisegment_part._multisegment)
            else:
                multipoint_part = EMPTY
            return from_mix_components(multipoint_part, multisegment_part,
                                       multipolygon_part)
        elif isinstance(other, (Shaped, Mix)):
            return (self._multipolygon | other
                    | self._multisegment | self._multipoint)
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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.
        """
        return ((other - self._multipoint) & (other - self._multisegment)
                & other - self._multipolygon)

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix - mix is EMPTY
        True
        """
        return from_mix_components(self._multipoint - other,
                                   self._multisegment - other,
                                   self._multipolygon - other)

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix ^ mix is EMPTY
        True
        """
        if isinstance(other, Multipoint):
            rest_other = other - self._multipolygon - self._multisegment
            return from_mix_components(self._multipoint ^ rest_other,
                                       self._multisegment,
                                       self._multipolygon)
        elif isinstance(other, Linear):
            multipoint_part, multisegment_part = (self._multipoint,
                                                  self._multisegment)
            multipolygon_part = self._multipolygon ^ other
            if isinstance(multipolygon_part, Linear):
                multisegment_part = (multisegment_part ^ multipolygon_part
                                     ^ multipoint_part)
                multipolygon_part = EMPTY
            elif isinstance(multipolygon_part, Mix):
                multisegment_part = (multisegment_part
                                     ^ multipolygon_part._multisegment
                                     ^ multipoint_part)
                multipolygon_part = multipolygon_part._multipolygon
            else:
                # other is subset of the multipolygon
                return from_mix_components(multipoint_part, multisegment_part,
                                           multipolygon_part)
            if isinstance(multisegment_part, Mix):
                multipoint_part, multisegment_part = (
                    multisegment_part._multipoint,
                    multisegment_part._multisegment)
            else:
                multipoint_part = EMPTY
            return from_mix_components(multipoint_part, multisegment_part,
                                       multipolygon_part)
        elif isinstance(other, (Shaped, Mix)):
            return (self._multipolygon ^ other
                    ^ self._multisegment ^ self._multipoint)
        else:
            return NotImplemented

    __rxor__ = __xor__

    @classmethod
    def from_raw(cls, raw: RawMix) -> 'Mix':
        """
        Constructs mix from the combination of Python built-ins.

        Time complexity:
            ``O(raw_elements_count)``
        Memory complexity:
            ``O(raw_elements_count)``

        where ``raw_elements_count = raw_multipoint_size +\
 raw_multisegment_size + raw_multipolygon_vertices_count``,
        ``raw_multipoint_size = len(raw_multipoint)``,
        ``raw_multisegment_size = len(raw_multisegment)``,
        ``raw_multipolygon_vertices_count = sum(len(raw_border)\
 + sum(len(raw_hole) for raw_hole in raw_holes)\
 for raw_border, raw_holes in raw_multipolygon)``,
        ``raw_multipoint, raw_multisegment, raw_multipolygon = raw``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> from gon.linear import Contour
        >>> (mix
        ...  == Mix(Multipoint(Point(3, 3), Point(7, 7)),
        ...         Multisegment(Segment(Point(0, 6), Point(0, 8)),
        ...                      Segment(Point(6, 6), Point(6, 8))),
        ...         Multipolygon(Polygon(Contour([Point(0, 0), Point(6, 0),
        ...                                       Point(6, 6), Point(0, 6)]),
        ...                      [Contour([Point(2, 2), Point(2, 4),
        ...                                Point(4, 4), Point(4, 2)])]))))
        True
        """
        raw_multipoint, raw_multisegment, raw_multipolygon = raw
        return cls(EMPTY
                   if raw_multipoint is RAW_EMPTY
                   else Multipoint.from_raw(raw_multipoint),
                   EMPTY
                   if raw_multisegment is RAW_EMPTY
                   else Multisegment.from_raw(raw_multisegment),
                   EMPTY
                   if raw_multipolygon is RAW_EMPTY
                   else Multipolygon.from_raw(raw_multipolygon))

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the mix.

        Time complexity:
            ``O(elements_count)``
        Memory complexity:
            ``O(1)``

        where ``elements_count = multisegment_size\
 if self.multipolygon is EMPTY else multipolygon_vertices_count``,
        ``multisegment_size = len(segments)``,
        ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``,
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.centroid == Point(3, 3)
        True
        """
        return (self._multisegment
                if self._multipolygon is EMPTY
                else self._multipolygon).centroid

    @property
    def multipoint(self) -> Maybe[Multipoint]:
        """
        Returns multipoint of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.multipoint == Multipoint(Point(3, 3), Point(7, 7))
        True
        """
        return self._multipoint

    @property
    def multipolygon(self) -> Maybe[Multipolygon]:
        """
        Returns multipolygon of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> from gon.linear import Contour
        >>> (mix.multipolygon
        ...  == Multipolygon(Polygon(Contour([Point(0, 0), Point(6, 0),
        ...                                   Point(6, 6), Point(0, 6)]),
        ...                  [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                            Point(4, 2)])])))
        True
        """
        return self._multipolygon

    @property
    def multisegment(self) -> Maybe[Multisegment]:
        """
        Returns multisegment of the mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.multisegment == Multisegment(Segment(Point(0, 6), Point(0, 8)),
        ...                                  Segment(Point(6, 6), Point(6, 8)))
        True
        """
        return self._multisegment

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.distance_to(mix) == 0
        True
        """
        candidates = (component.distance_to(other)
                      for component in self._components
                      if component is not EMPTY)
        result = next(candidates)
        if not result:
            return result
        for candidate in candidates:
            if not candidate:
                return candidate
            elif candidate < result:
                result = candidate
        return result

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.index()
        """
        if self._multisegment is not EMPTY:
            self._multisegment.index()
        if self._multipolygon is not EMPTY:
            self._multipolygon.index()

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
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

    def raw(self) -> RawMix:
        """
        Returns the mix as combination of Python built-ins.

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.raw()
        ([(3, 3), (7, 7)], [((0, 6), (0, 8)), ((6, 6), (6, 8))],\
 [([(0, 0), (6, 0), (6, 6), (0, 6)], [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        """
        return (self._multipoint.raw(), self._multisegment.raw(),
                self._multipolygon.raw())

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.rotate(1, 0) == mix
        True
        >>> (mix.rotate(0, 1, Point(1, 1))
        ...  == Mix.from_raw(([(-1, 3), (-5, 7)],
        ...                   [((-4, 0), (-6, 0)), ((-4, 6), (-6, 6))],
        ...                   [([(2, 0), (2, 6), (-4, 6), (-4, 0)],
        ...                     [[(0, 2), (-2, 2), (-2, 4), (0, 4)]])])))
        True
        """
        return Mix(self._multipoint.rotate(cosine, sine, point),
                   self._multisegment.rotate(cosine, sine, point),
                   self._multipolygon.rotate(cosine, sine, point))

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.scale(1) == mix
        True
        >>> (mix.scale(1, 2)
        ...  == Mix.from_raw(([(3, 6), (7, 14)],
        ...                   [((0, 12), (0, 16)), ((6, 12), (6, 16))],
        ...                   [([(0, 0), (6, 0), (6, 12), (0, 12)],
        ...                     [[(2, 4), (2, 8), (4, 8), (4, 4)]])])))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        return (Mix(self._multipoint.scale(factor_x, factor_y),
                    self._multisegment.scale(factor_x, factor_y),
                    self._multipolygon.scale(factor_x, factor_y))
                if factor_x and factor_y
                else ((self._multipoint.scale(factor_x, factor_y)
                       | self._multisegment.scale(factor_x, factor_y)
                       | self._multipolygon.scale(factor_x, factor_y))
                      if factor_x or factor_y
                      else Multipoint(Point(factor_x, factor_y))))

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> (mix.translate(1, 2)
        ...  == Mix.from_raw(([(4, 5), (8, 9)],
        ...                   [((1, 8), (1, 10)), ((7, 8), (7, 10))],
        ...                   [([(1, 2), (7, 2), (7, 8), (1, 8)],
        ...                     [[(3, 4), (3, 6), (5, 6), (5, 4)]])])))
        True
        """
        return Mix(self._multipoint.translate(step_x, step_y),
                   self._multisegment.translate(step_x, step_y),
                   self._multipolygon.translate(step_x, step_y))

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
        ``segments = [] if self.multisegment is EMPTY\
 else self.multisegment.segments``,
        ``polygons = [] if self.multipolygon is EMPTY\
 else self.multipolygon.polygons``.

        >>> mix = Mix.from_raw(([(3, 3), (7, 7)],
        ...                     [((0, 6), (0, 8)), ((6, 6), (6, 8))],
        ...                     [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                       [[(2, 2), (2, 4), (4, 4), (4, 2)]])]))
        >>> mix.validate()
        """
        if (sum(component is not EMPTY for component in self._components)
                < MIN_MIX_NON_EMPTY_COMPONENTS):
            raise ValueError('At least {count} components should not be empty.'
                             .format(count=MIN_MIX_NON_EMPTY_COMPONENTS))
        for component in self._components:
            component.validate()
        if (not self._multipoint.disjoint(self._multisegment)
                or not self._multipoint.disjoint(self._multipolygon)):
            raise ValueError('Multipoint should be disjoint '
                             'with other components.')
        multipolygon_multisegment_relation = self._multipolygon.relate(
                self._multisegment)
        if multipolygon_multisegment_relation in (Relation.CROSS,
                                                  Relation.COMPONENT,
                                                  Relation.ENCLOSED,
                                                  Relation.WITHIN):
            raise ValueError('Multisegment should not {} multipolygon.'
                             .format('cross'
                                     if (multipolygon_multisegment_relation
                                         is Relation.CROSS)
                                     else 'be subset of'))
        elif (multipolygon_multisegment_relation is Relation.TOUCH
              and any(polygon.border.relate(self._multisegment)
                      in (Relation.OVERLAP,
                          Relation.COMPOSITE)
                      or any(hole.relate(self._multisegment)
                             in (Relation.OVERLAP,
                                 Relation.COMPOSITE)
                             for hole in polygon.holes)
                      for polygon in self._multipolygon.polygons)):
            raise ValueError('Multisegment should not overlap '
                             'multipolygon borders.')

    def _relate_linear(self, other: Linear) -> Relation:
        if self._multipolygon is EMPTY:
            multisegment_relation = self._multisegment.relate(other)
            if multisegment_relation is Relation.DISJOINT:
                multipoint_relation = self._multipoint.relate(other)
                return (Relation.TOUCH
                        if multipoint_relation is Relation.COMPOSITE
                        else multipoint_relation)
            elif multisegment_relation is Relation.COMPOSITE:
                multipoint_relation = self._multipoint.relate(other)
                return (multisegment_relation
                        if multipoint_relation is multisegment_relation
                        else Relation.OVERLAP)
            else:
                return (Relation.COMPONENT
                        if multisegment_relation is Relation.EQUAL
                        else multisegment_relation)
        else:
            multipolygon_relation = self._multipolygon.relate(other)
            if multipolygon_relation is Relation.DISJOINT:
                multisegment_relation = self._multisegment.relate(other)
                if multisegment_relation is Relation.DISJOINT:
                    multipoint_relation = self._multipoint.relate(other)
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
                rest_other = other - self._multipolygon
                multisegment_relation = self._multisegment.relate(rest_other)
                return (Relation.COMPONENT
                        if (multisegment_relation is Relation.EQUAL
                            or multisegment_relation is Relation.COMPONENT)
                        else multipolygon_relation)
            else:
                return multipolygon_relation

    def _relate_mix(self, other: 'Mix') -> Relation:
        if self._multipolygon is other._multipolygon is EMPTY:
            multisegments_relation = self._multisegment.relate(
                    other._multisegment)
            if multisegments_relation is Relation.DISJOINT:
                return (multisegments_relation
                        if (self._relate_multipoint(other._multipoint)
                            is other._relate_multipoint(self._multipoint)
                            is multisegments_relation)
                        else Relation.TOUCH)
            elif multisegments_relation is Relation.COMPOSITE:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint)
                return (multisegments_relation
                        if multipoint_relation is Relation.COMPONENT
                        else Relation.OVERLAP)
            elif multisegments_relation is Relation.EQUAL:
                other_multipoint_relation = self._multipoint.relate(
                        other._multipoint)
                return (Relation.OVERLAP
                        if other_multipoint_relation is Relation.DISJOINT
                        else other_multipoint_relation)
            elif multisegments_relation is Relation.COMPONENT:
                other_multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                return (multisegments_relation
                        if other_multipoint_relation is Relation.COMPONENT
                        else Relation.OVERLAP)
            else:
                return multisegments_relation
        elif self._multipolygon is EMPTY:
            multisegment_relation = other._relate_linear(
                    self._multisegment)
            if multisegment_relation is Relation.CROSS:
                return multisegment_relation
            multipoint_relation = other._relate_multipoint(
                    self._multipoint)
            if multisegment_relation is Relation.DISJOINT:
                return (multipoint_relation
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else (Relation.TOUCH
                              if multipoint_relation is Relation.COMPONENT
                              else Relation.CROSS))
            elif multisegment_relation is Relation.TOUCH:
                return (Relation.CROSS
                        if multipoint_relation in (Relation.CROSS,
                                                   Relation.ENCLOSED,
                                                   Relation.WITHIN)
                        else multisegment_relation)
            elif multisegment_relation is Relation.COMPONENT:
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
        elif other._multipolygon is EMPTY:
            other_multisegment_relation = self._relate_linear(
                    other._multisegment)
            if other_multisegment_relation is Relation.CROSS:
                return other_multisegment_relation
            other_multipoint_relation = self._relate_multipoint(
                    other._multipoint)
            if other_multisegment_relation is Relation.DISJOINT:
                return (other_multipoint_relation
                        if other_multipoint_relation in (Relation.DISJOINT,
                                                         Relation.TOUCH,
                                                         Relation.CROSS)
                        else
                        (Relation.TOUCH
                         if other_multipoint_relation is Relation.COMPONENT
                         else Relation.CROSS))
            elif other_multisegment_relation is Relation.TOUCH:
                return (Relation.CROSS
                        if other_multipoint_relation in (Relation.CROSS,
                                                         Relation.ENCLOSED,
                                                         Relation.WITHIN)
                        else other_multisegment_relation)
            elif other_multisegment_relation is Relation.COMPONENT:
                return (Relation.TOUCH
                        if (other_multipoint_relation is Relation.DISJOINT
                            or other_multipoint_relation is Relation.TOUCH)
                        else (other_multipoint_relation
                              if (other_multipoint_relation is Relation.CROSS
                                  or (other_multipoint_relation
                                      is Relation.COMPONENT))
                              else Relation.ENCLOSED))
            elif other_multisegment_relation is Relation.ENCLOSED:
                return (Relation.CROSS
                        if other_multipoint_relation in (Relation.DISJOINT,
                                                         Relation.TOUCH,
                                                         Relation.CROSS)
                        else other_multisegment_relation)
            else:
                return (Relation.CROSS
                        if other_multipoint_relation in (Relation.DISJOINT,
                                                         Relation.TOUCH,
                                                         Relation.CROSS)
                        else
                        (Relation.ENCLOSED
                         if other_multipoint_relation is Relation.COMPONENT
                         else other_multisegment_relation))
        multipolygons_relation = self._multipolygon.relate(
                other._multipolygon)
        if (multipolygons_relation is Relation.DISJOINT
                or multipolygons_relation is Relation.TOUCH):
            if self._multisegment is other._multisegment is EMPTY:
                other_multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                if other_multipoint_relation is Relation.CROSS:
                    return other_multipoint_relation
                elif (other_multipoint_relation is Relation.ENCLOSED
                      or other_multipoint_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    multipoint_relation = other._relate_multipoint(
                            self._multipoint)
                    if (multipoint_relation
                            is other_multipoint_relation
                            is Relation.DISJOINT):
                        return multipolygons_relation
                    elif multipoint_relation is Relation.CROSS:
                        return multipoint_relation
                    elif (multipoint_relation is Relation.ENCLOSED
                          or multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    else:
                        return Relation.TOUCH
            elif self._multisegment is EMPTY:
                other_multisegment_relation = self._relate_linear(
                        other._multisegment)
                if other_multisegment_relation is Relation.CROSS:
                    return other_multisegment_relation
                elif (other_multisegment_relation is Relation.ENCLOSED
                      or other_multisegment_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    multipoint_relation = other._relate_multipoint(
                            self._multipoint)
                    if multipoint_relation is Relation.CROSS:
                        return multipoint_relation
                    elif (multipoint_relation is Relation.ENCLOSED
                          or multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif other._multipoint is EMPTY:
                        return (multipolygons_relation
                                if (multipoint_relation
                                    is other_multisegment_relation
                                    is Relation.DISJOINT)
                                else Relation.TOUCH)
                    else:
                        other_multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        if other_multipoint_relation is Relation.CROSS:
                            return other_multipoint_relation
                        elif (other_multipoint_relation is Relation.ENCLOSED
                              or other_multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        elif (multipoint_relation
                              is other_multipoint_relation
                              is other_multisegment_relation
                              is Relation.DISJOINT):
                            return multipolygons_relation
                        else:
                            return Relation.TOUCH
            elif other._multisegment is EMPTY:
                multisegment_relation = other._relate_linear(
                        self._multisegment)
                if multisegment_relation is Relation.CROSS:
                    return multisegment_relation
                elif (multisegment_relation is Relation.ENCLOSED
                      or multisegment_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    other_multipoint_relation = self._relate_multipoint(
                            other._multipoint)
                    if other_multipoint_relation is Relation.CROSS:
                        return other_multipoint_relation
                    elif (other_multipoint_relation is Relation.ENCLOSED
                          or other_multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif self._multipoint is EMPTY:
                        return (multipolygons_relation
                                if (multisegment_relation
                                    is other_multipoint_relation
                                    is Relation.DISJOINT)
                                else Relation.TOUCH)
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self._multipoint)
                        if multipoint_relation is Relation.CROSS:
                            return multipoint_relation
                        elif (multipoint_relation is Relation.ENCLOSED
                              or multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        elif (multipoint_relation
                              is multisegment_relation
                              is other_multipoint_relation
                              is Relation.DISJOINT):
                            return multipolygons_relation
                        else:
                            return Relation.TOUCH
            else:
                other_multisegment_relation = self._relate_linear(
                        other._multisegment)
                if other_multisegment_relation is Relation.CROSS:
                    return other_multisegment_relation
                elif (other_multisegment_relation is Relation.ENCLOSED
                      or other_multisegment_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    multisegment_relation = other._relate_linear(
                            self._multisegment)
                    if multisegment_relation is Relation.CROSS:
                        return multisegment_relation
                    elif (multisegment_relation is Relation.ENCLOSED
                          or multisegment_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif self._multipoint is EMPTY:
                        other_multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        return (other_multipoint_relation
                                if other_multipoint_relation is Relation.CROSS
                                else
                                (Relation.CROSS
                                 if (other_multipoint_relation
                                     is Relation.ENCLOSED
                                     or other_multipoint_relation
                                     is Relation.WITHIN)
                                 else (multipolygons_relation
                                       if (other_multipoint_relation
                                           is multisegment_relation
                                           is other_multisegment_relation
                                           is Relation.DISJOINT)
                                       else Relation.TOUCH)))
                    elif other._multipoint is EMPTY:
                        multipoint_relation = other._relate_multipoint(
                                self._multipoint)
                        return (multipoint_relation
                                if multipoint_relation is Relation.CROSS
                                else
                                (Relation.CROSS
                                 if (multipoint_relation is Relation.ENCLOSED
                                     or multipoint_relation is Relation.WITHIN)
                                 else (multipolygons_relation
                                       if (multipoint_relation
                                           is multisegment_relation
                                           is other_multisegment_relation
                                           is Relation.DISJOINT)
                                       else Relation.TOUCH)))
                    else:
                        other_multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        if other_multipoint_relation is Relation.CROSS:
                            return other_multipoint_relation
                        elif (other_multipoint_relation is Relation.ENCLOSED
                              or other_multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        else:
                            multipoint_relation = other._relate_multipoint(
                                    self._multipoint)
                            return (multipoint_relation
                                    if multipoint_relation is Relation.CROSS
                                    else (Relation.CROSS
                                          if (multipoint_relation
                                              is Relation.ENCLOSED
                                              or multipoint_relation
                                              is Relation.WITHIN)
                                          else
                                          (multipolygons_relation
                                           if (multipoint_relation
                                               is multisegment_relation
                                               is other_multipoint_relation
                                               is other_multisegment_relation
                                               is Relation.DISJOINT)
                                           else Relation.TOUCH)))
        elif multipolygons_relation in (Relation.COVER,
                                        Relation.ENCLOSES,
                                        Relation.COMPOSITE):
            if self._multisegment is EMPTY:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint).complement
                return (multipolygons_relation
                        if multipoint_relation is multipolygons_relation
                        else (Relation.ENCLOSES
                              if multipoint_relation in (Relation.COVER,
                                                         Relation.ENCLOSES,
                                                         Relation.COMPOSITE)
                              else Relation.OVERLAP))
            else:
                multisegment_relation = other._relate_linear(
                        self._multisegment).complement
                if multisegment_relation is multipolygons_relation:
                    if self._multipoint is EMPTY:
                        return multipolygons_relation
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self._multipoint).complement
                        return (multipolygons_relation
                                if (multipoint_relation
                                    is multipolygons_relation)
                                else
                                (Relation.ENCLOSES
                                 if multipoint_relation in (Relation.COVER,
                                                            Relation.ENCLOSES,
                                                            Relation.COMPOSITE)
                                 else Relation.OVERLAP))
                elif multisegment_relation in (Relation.COVER,
                                               Relation.ENCLOSES,
                                               Relation.COMPOSITE):
                    if self._multipoint is EMPTY:
                        return Relation.ENCLOSES
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self._multipoint).complement
                        return (Relation.ENCLOSES
                                if multipoint_relation in (Relation.COVER,
                                                           Relation.ENCLOSES,
                                                           Relation.COMPOSITE)
                                else Relation.OVERLAP)
                else:
                    return Relation.OVERLAP
        elif multipolygons_relation is Relation.EQUAL:
            multisegments_relation = self._multisegment.relate(
                    other._multisegment)
            if self._multisegment is other._multisegment is EMPTY:
                multipoints_relation = self._multipoint.relate(
                        other._multipoint)
                return (multipolygons_relation
                        if (self._multipoint is other._multipoint is EMPTY
                            or multipoints_relation is Relation.EQUAL)
                        else
                        (multipoints_relation
                         if (multipoints_relation is Relation.COMPOSITE
                             or multipoints_relation is Relation.COMPONENT)
                         else Relation.OVERLAP))
            elif self._multisegment is EMPTY:
                multipoints_relation = other._relate_multipoint(
                        self._multipoint)
                return (Relation.COMPOSITE
                        if (multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            elif other._multisegment is EMPTY:
                multipoints_relation = self._relate_multipoint(
                        other._multipoint)
                return (Relation.COMPONENT
                        if (multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            elif multisegments_relation is Relation.COMPOSITE:
                multipoints_relation = other._relate_multipoint(
                        self._multipoint)
                return (multisegments_relation
                        if (self._multipoint is EMPTY
                            or multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            elif multisegments_relation is Relation.EQUAL:
                multipoints_relation = self._multipoint.relate(
                        other._multipoint)
                return (multipolygons_relation
                        if (self._multipoint is other._multipoint is EMPTY
                            or multipoints_relation is Relation.EQUAL)
                        else
                        (Relation.COMPOSITE
                         if self._multipoint is EMPTY
                         else
                         (Relation.COMPONENT
                          if other._multipoint is EMPTY
                          else
                          (multipoints_relation
                           if (multipoints_relation is Relation.COMPONENT
                               or multipoints_relation is Relation.COMPOSITE)
                           else Relation.OVERLAP))))
            elif multisegments_relation is Relation.COMPONENT:
                multipoints_relation = self._relate_multipoint(
                        other._multipoint)
                return (multisegments_relation
                        if (other._multipoint is EMPTY
                            or multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            else:
                return Relation.OVERLAP
        elif multipolygons_relation in (Relation.COMPONENT,
                                        Relation.ENCLOSED,
                                        Relation.WITHIN):
            if other._multisegment is EMPTY:
                multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                return (multipolygons_relation
                        if multipoint_relation is multipolygons_relation
                        else (Relation.ENCLOSED
                              if multipoint_relation in (Relation.COMPONENT,
                                                         Relation.ENCLOSED,
                                                         Relation.WITHIN)
                              else Relation.OVERLAP))
            else:
                multisegment_relation = self._relate_linear(
                        other._multisegment)
                if multisegment_relation is multipolygons_relation:
                    if other._multipoint is EMPTY:
                        return multipolygons_relation
                    else:
                        multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        return (multipolygons_relation
                                if (multipoint_relation
                                    is multipolygons_relation)
                                else
                                (Relation.ENCLOSED
                                 if multipoint_relation in (Relation.COMPONENT,
                                                            Relation.ENCLOSED,
                                                            Relation.WITHIN)
                                 else Relation.OVERLAP))
                elif multisegment_relation in (Relation.COMPONENT,
                                               Relation.ENCLOSED,
                                               Relation.WITHIN):
                    if other._multipoint is EMPTY:
                        return Relation.ENCLOSED
                    else:
                        multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        return (Relation.ENCLOSED
                                if multipoint_relation in (Relation.COMPONENT,
                                                           Relation.ENCLOSED,
                                                           Relation.WITHIN)
                                else Relation.OVERLAP)
                else:
                    return Relation.OVERLAP
        else:
            return multipolygons_relation

    def _relate_multipoint(self, other: Multipoint) -> Relation:
        if self._multipolygon is EMPTY:
            multisegment_relation = self._multisegment.relate(other)
            if multisegment_relation is Relation.DISJOINT:
                multipoint_relation = self._multipoint.relate(other)
                return (multipoint_relation
                        if multipoint_relation is Relation.DISJOINT
                        else (Relation.COMPONENT
                              if (multipoint_relation is Relation.COMPONENT
                                  or multipoint_relation is Relation.EQUAL)
                              else Relation.TOUCH))
            elif multisegment_relation is Relation.TOUCH:
                rest_other = other - self._multisegment
                multipoint_relation = self._multipoint.relate(rest_other)
                return (Relation.COMPONENT
                        if (multipoint_relation is Relation.EQUAL
                            or multipoint_relation is Relation.COMPONENT)
                        else multisegment_relation)
            else:
                return multisegment_relation
        else:
            multipolygon_relation = self._multipolygon.relate(other)
            if multipolygon_relation in (Relation.COMPONENT,
                                         Relation.ENCLOSED,
                                         Relation.WITHIN):
                return multipolygon_relation
            elif (multipolygon_relation is Relation.TOUCH
                  or multipolygon_relation is Relation.CROSS):
                rest_other = other - self._multipolygon
                if self._multisegment is EMPTY:
                    multipoint_relation = self._multipoint.relate(rest_other)
                    return (Relation.COMPONENT
                            if (multipoint_relation is Relation.EQUAL
                                or multipoint_relation is Relation.COMPONENT)
                            else multipolygon_relation)
                else:
                    multisegment_relation = self._multisegment.relate(
                            rest_other)
                    if multisegment_relation is Relation.DISJOINT:
                        multipoint_relation = self._multipoint.relate(
                                rest_other)
                        return ((Relation.COMPONENT
                                 if multipolygon_relation is Relation.TOUCH
                                 else Relation.ENCLOSED)
                                if (multipoint_relation is Relation.COMPONENT
                                    or multipoint_relation is Relation.EQUAL)
                                else multipolygon_relation)
                    elif multisegment_relation is Relation.TOUCH:
                        rest_other -= self._multisegment
                        multipoint_relation = self._multipoint.relate(
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
                multisegment_relation = self._multisegment.relate(other)
                if multisegment_relation is Relation.DISJOINT:
                    multipoint_relation = self._multipoint.relate(other)
                    return (multipolygon_relation
                            if multipoint_relation is Relation.DISJOINT
                            else (Relation.COMPONENT
                                  if (multipoint_relation is Relation.COMPONENT
                                      or multipoint_relation is Relation.EQUAL)
                                  else Relation.TOUCH))
                elif multisegment_relation is Relation.TOUCH:
                    rest_other = other - self._multisegment
                    multipoint_relation = self._multipoint.relate(rest_other)
                    return (multipolygon_relation
                            if multipoint_relation is Relation.DISJOINT
                            else (Relation.COMPONENT
                                  if (multipoint_relation is Relation.COMPONENT
                                      or multipoint_relation is Relation.EQUAL)
                                  else Relation.TOUCH))
                else:
                    return multisegment_relation

    def _relate_shaped(self, other: Shaped) -> Relation:
        if self._multipolygon is EMPTY:
            multisegment_relation = self._multisegment.relate(other)
            if (multisegment_relation is Relation.DISJOINT
                    or multisegment_relation is Relation.TOUCH):
                multipoint_relation = self._multipoint.relate(other)
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
                multipoint_relation = self._multipoint.relate(other)
                return (Relation.CROSS
                        if (multipoint_relation is Relation.DISJOINT
                            or multipoint_relation is Relation.TOUCH)
                        else (multipoint_relation
                              if (multipoint_relation is multisegment_relation
                                  or multipoint_relation is Relation.CROSS)
                              else Relation.ENCLOSES))
            elif multisegment_relation is Relation.COMPOSITE:
                multipoint_relation = self._multipoint.relate(other)
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
            multipolygon_relation = self._multipolygon.relate(other)
            if multipolygon_relation is Relation.DISJOINT:
                multisegment_relation = self._multisegment.relate(other)
                if multisegment_relation is Relation.DISJOINT:
                    multipoint_relation = self._multipoint.relate(other)
                    return (multipoint_relation
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                            else (Relation.TOUCH
                                  if multipoint_relation is Relation.COMPOSITE
                                  else Relation.CROSS))
                elif (multisegment_relation is Relation.TOUCH
                      or multisegment_relation is Relation.COMPOSITE):
                    multipoint_relation = self._multipoint.relate(other)
                    return (Relation.TOUCH
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.COMPOSITE)
                            else Relation.CROSS)
                else:
                    return Relation.CROSS
            elif multipolygon_relation is Relation.TOUCH:
                multisegment_relation = self._multisegment.relate(other)
                if multisegment_relation in (Relation.DISJOINT,
                                             Relation.TOUCH,
                                             Relation.COMPOSITE):
                    multipoint_relation = self._multipoint.relate(other)
                    return (multipolygon_relation
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.COMPOSITE)
                            else Relation.CROSS)
                else:
                    return Relation.CROSS
            elif (multipolygon_relation is Relation.COVER
                  or multipolygon_relation is Relation.COMPOSITE):
                if self._multisegment is EMPTY:
                    multipoint_relation = self._multipoint.relate(other)
                    return (Relation.OVERLAP
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                            else (multipolygon_relation
                                  if (multipoint_relation
                                      is multipolygon_relation)
                                  else Relation.ENCLOSES))
                else:
                    multisegment_relation = self._multisegment.relate(other)
                    if multisegment_relation in (Relation.DISJOINT,
                                                 Relation.TOUCH,
                                                 Relation.CROSS):
                        return Relation.OVERLAP
                    elif self._multipoint is EMPTY:
                        return (multipolygon_relation
                                if (multisegment_relation
                                    is multipolygon_relation)
                                else Relation.ENCLOSES)
                    else:
                        multipoint_relation = self._multipoint.relate(other)
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
                if self._multisegment is EMPTY:
                    multipoint_relation = self._multipoint.relate(other)
                    return (Relation.OVERLAP
                            if multipoint_relation in (Relation.DISJOINT,
                                                       Relation.TOUCH,
                                                       Relation.CROSS)
                            else Relation.ENCLOSES)
                else:
                    multisegment_relation = self._multisegment.relate(other)
                    if multisegment_relation in (Relation.DISJOINT,
                                                 Relation.TOUCH,
                                                 Relation.CROSS):
                        return Relation.OVERLAP
                    elif self._multipoint is EMPTY:
                        return multipolygon_relation
                    else:
                        multipoint_relation = self._multipoint.relate(other)
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
    return (Mix(multipoint,
                Multisegment(linear)
                if isinstance(linear, Segment)
                else linear,
                Multipolygon(shaped)
                if isinstance(shaped, Polygon)
                else shaped)
            if (((multipoint is not EMPTY)
                 + (linear is not EMPTY)
                 + (shaped is not EMPTY))
                >= MIN_MIX_NON_EMPTY_COMPONENTS)
            else (multipoint
                  if multipoint is not EMPTY
                  else (linear
                        if linear is not EMPTY
                        else shaped)))
