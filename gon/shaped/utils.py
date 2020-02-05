from operator import attrgetter
from typing import (Iterable,
                    List,
                    Sequence)

from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
from gon.linear import (Segment,
                        to_segment)
from .hints import Contour


def to_angles(contour: Contour) -> Iterable[Angle]:
    return (Angle(contour[index - 1],
                  contour[index],
                  contour[(index + 1) % len(contour)])
            for index in range(len(contour)))


def to_edges(contour: Contour) -> Iterable[Segment]:
    return (to_segment(contour[index], contour[(index + 1) % len(contour)])
            for index in range(len(contour)))


def to_convex_hull(points: Sequence[Point]) -> List[Point]:
    points = sorted(points,
                    key=attrgetter('x', 'y'))
    lower = _to_sub_hull(points)
    upper = _to_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_sub_hull(points: Iterable[Point]) -> List[Point]:
    result = []
    for point in points:
        while len(result) >= 2:
            if (Angle(result[-1], result[-2], point).orientation
                    is not Orientation.COUNTERCLOCKWISE):
                del result[-1]
            else:
                break
        result.append(point)
    return result
