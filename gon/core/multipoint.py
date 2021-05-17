from functools import partial
from typing import (AbstractSet,
                    Iterable,
                    List,
                    Optional,
                    Sequence)

from ground.base import (Context,
                         get_context)
from locus import kd
from reprit.base import generate_repr

from .compound import (Compound,
                       Indexable,
                       Location,
                       Relation)
from .empty import EMPTY
from .geometry import Geometry
from .hints import Scalar
from .iterable import (non_negative_min,
                       unique_ever_seen)
from .point import (Point,
                    point_to_step,
                    rotate_point_around_origin,
                    rotate_translate_point,
                    scale_point)


class Multipoint(Indexable):
    __slots__ = '_context', '_points', '_points_set', '_nearest_point'

    def __init__(self, points: Sequence[Point]) -> None:
        """
        Initializes multipoint.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(points)``.
        """
        context = get_context()
        self._context = context
        self._points, self._points_set = points, frozenset(points)
        self._nearest_point = partial(_to_nearest_point, context, points)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the multipoint with the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint & multipoint == multipoint
        True
        """
        return (pack_points(self._points_set & other._points_set
                            if isinstance(other, Multipoint)
                            else [point
                                  for point in self._points
                                  if point in other])
                if isinstance(other, Compound)
                else NotImplemented)

    __rand__ = __and__

    def __contains__(self, point: Point) -> bool:
        """
        Checks if the multipoint contains the point.

        Time complexity:
            ``O(1)`` expected,
            ``O(len(self.points))`` worst
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> all(point in multipoint for point in multipoint.points)
        True
        """
        return point in self._points_set

    def __eq__(self, other: 'Multipoint') -> bool:
        """
        Checks if multipoints are equal.

        Time complexity:
            ``O(min(len(self.points), len(other.points)))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint == multipoint
        True
        >>> multipoint == Multipoint([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                           Point(0, 1)])
        False
        >>> multipoint == Multipoint([Point(1, 0), Point(0, 0), Point(0, 1)])
        True
        """
        return self is other or (self._points_set == other._points_set
                                 if isinstance(other, Multipoint)
                                 else NotImplemented)

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the multipoint is a superset of the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint >= multipoint
        True
        >>> multipoint >= Multipoint([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                           Point(0, 1)])
        False
        >>> multipoint >= Multipoint([Point(1, 0), Point(0, 0), Point(0, 1)])
        True
        """
        return (self._points_set >= other._points_set
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the multipoint is a strict superset of the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint > multipoint
        False
        >>> multipoint > Multipoint([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                          Point(0, 1)])
        False
        >>> multipoint > Multipoint([Point(1, 0), Point(0, 0), Point(0, 1)])
        False
        """
        return (self._points_set > other._points_set
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __hash__(self) -> int:
        """
        Returns hash value of the multipoint.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> hash(multipoint) == hash(multipoint)
        True
        """
        return hash(self._points_set)

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the multipoint is a subset of the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint <= multipoint
        True
        >>> multipoint <= Multipoint([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                           Point(0, 1)])
        True
        >>> multipoint <= Multipoint([Point(1, 0), Point(0, 0), Point(0, 1)])
        True
        """
        return (self._points_set <= other._points_set
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the multipoint is a strict subset of the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint < multipoint
        False
        >>> multipoint < Multipoint([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                          Point(0, 1)])
        True
        >>> multipoint < Multipoint([Point(1, 0), Point(0, 0), Point(0, 1)])
        False
        """
        return (self._points_set < other._points_set
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the multipoint with the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint | multipoint == multipoint
        True
        """
        return (Multipoint(list(self._points_set | other._points_set))
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the multipoint with the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint - multipoint is EMPTY
        True
        """
        return (pack_points(self._points_set - other._points_set
                            if isinstance(other, Multipoint)
                            else [point
                                  for point in self._points
                                  if point not in other])
                if isinstance(other, Compound)
                else NotImplemented)

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the multipoint with the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint ^ multipoint is EMPTY
        True
        """
        return (pack_points(self._points_set ^ other._points_set)
                if isinstance(other, Multipoint)
                else NotImplemented)

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the multipoint.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(3, 0), Point(0, 3)])
        >>> multipoint.centroid == Point(1, 1)
        True
        """
        return self.context.multipoint_centroid(self)

    @property
    def context(self) -> Context:
        """
        Returns context of the multipoint.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(3, 0), Point(0, 3)])
        >>> isinstance(multipoint.context, Context)
        True
        """
        return self._context

    @property
    def points(self) -> List[Point]:
        """
        Returns points of the multipoint.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint.points
        [Point(0, 0), Point(1, 0), Point(0, 1)]
        """
        return list(self._points)

    def distance_to(self, other: Geometry) -> Scalar:
        """
        Returns distance between the multipoint and the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint.distance_to(multipoint) == 0
        True
        """
        return (self._distance_to_point(other)
                if isinstance(other, Point)
                else (non_negative_min(self._distance_to_point(point)
                                       for point in other.points)
                      if isinstance(other, Multipoint)
                      else other.distance_to(self)))

    def index(self) -> None:
        """
        Pre-processes the multipoint to potentially improve queries.

        Time complexity:
            ``O(points_count * log points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint.index()
        """
        self._nearest_point = kd.Tree(self._points).nearest_point

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the multipoint.

        Time complexity:
            ``O(1)`` expected,
            ``O(len(self.points))`` worst
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> all(multipoint.locate(point) is Location.BOUNDARY
        ...     for point in multipoint.points)
        True
        """
        return (Location.BOUNDARY
                if point in self._points_set
                else Location.EXTERIOR)

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the multipoint and the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint.relate(multipoint) is Relation.EQUAL
        True
        """
        return ((Relation.EQUAL
                 if self is other
                 else _relate_sets(self._points_set, other._points_set))
                if isinstance(other, Multipoint)
                else self._relate_geometry(other))

    def rotate(self,
               cosine: Scalar,
               sine: Scalar,
               point: Optional[Point] = None) -> 'Multipoint':
        """
        Rotates geometric object by given cosine & sine around given point.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint.rotate(1, 0) == multipoint
        True
        >>> (multipoint.rotate(0, 1, Point(1, 1))
        ...  == Multipoint([Point(2, 0), Point(2, 1), Point(1, 0)]))
        True
        """
        return (Multipoint(rotate_points_around_origin(self._points, cosine,
                                                       sine))
                if point is None
                else
                Multipoint(rotate_translate_points(
                        self._points, cosine, sine,
                        *point_to_step(point, cosine, sine))))

    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> 'Multipoint':
        """
        Scales the multipoint by given factor.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint.scale(1) == multipoint
        True
        >>> (multipoint.scale(1, 2)
        ...  == Multipoint([Point(0, 0), Point(1, 0), Point(0, 2)]))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        return (Multipoint([scale_point(point, factor_x, factor_y)
                            for point in self._points])
                if factor_x and factor_y
                else
                (Multipoint(list(unique_ever_seen(scale_point(point, factor_x,
                                                              factor_y)
                                                  for point in self._points)))
                 if factor_x or factor_y
                 else Multipoint([Point(factor_x, factor_y)])))

    def translate(self,
                  step_x: Scalar,
                  step_y: Scalar) -> 'Multipoint':
        """
        Translates the multipoint by given step.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> (multipoint.translate(1, 2)
        ...  == Multipoint([Point(1, 2), Point(2, 2), Point(1, 3)]))
        True
        """
        return Multipoint([point.translate(step_x, step_y)
                           for point in self._points])

    def validate(self) -> None:
        """
        Checks if the multipoint is valid.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> multipoint.validate()
        """
        points = self._points
        if not points:
            raise ValueError('Multipoint is empty.')
        elif len(points) > len(self._points_set):
            raise ValueError('Duplicate points found.')
        for point in points:
            point.validate()

    def _distance_to_point(self, other: Point) -> Scalar:
        return self.context.sqrt(self.context.points_squared_distance(
                self._nearest_point(other), other))

    def _relate_geometry(self, other: Compound) -> Relation:
        disjoint = is_subset = not_interior = not_boundary = True
        for point in self._points:
            location = other.locate(point)
            if location is Location.INTERIOR:
                if disjoint:
                    disjoint = False
                if not_interior:
                    not_interior = False
            elif location is Location.BOUNDARY:
                if disjoint:
                    disjoint = False
                if not_boundary:
                    not_boundary = True
            elif is_subset:
                is_subset = False
        return (Relation.DISJOINT
                if disjoint
                else ((Relation.COMPOSITE
                       if is_subset
                       else Relation.TOUCH)
                      if not_interior
                      else ((Relation.COVER
                             if not_boundary
                             else Relation.ENCLOSES)
                            if is_subset
                            else Relation.CROSS)))


def pack_points(points: AbstractSet[Point]) -> Compound:
    return Multipoint(list(points)) if points else EMPTY


def rotate_points_around_origin(points: Iterable[Point],
                                cosine: Scalar,
                                sine: Scalar) -> List[Point]:
    return [rotate_point_around_origin(point, cosine, sine)
            for point in points]


def rotate_translate_points(points: Iterable[Point],
                            cosine: Scalar,
                            sine: Scalar,
                            step_x: Scalar,
                            step_y: Scalar) -> List[Point]:
    return [rotate_translate_point(point, cosine, sine, step_x, step_y)
            for point in points]


def _relate_sets(left: AbstractSet, right: AbstractSet) -> Relation:
    if left == right:
        return Relation.EQUAL
    intersection = left & right
    return ((Relation.COMPONENT
             if intersection == right
             else (Relation.COMPOSITE
                   if intersection == left
                   else Relation.OVERLAP))
            if intersection
            else Relation.DISJOINT)


def _to_nearest_point(context: Context,
                      points: Sequence[Point],
                      point: Point) -> Point:
    return min(points,
               key=partial(context.points_squared_distance, point))
