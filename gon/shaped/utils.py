from typing import (Iterable,
                    List,
                    Sequence)

from gon.angular import (Orientation,
                         to_orientation)
from gon.compound import Compound
from gon.degenerate import EMPTY
from gon.primitive import Point
from .hints import RawMultipolygon


def to_convex_hull(points: Sequence[Point]) -> List[Point]:
    points = sorted(points)
    lower = _to_sub_hull(points)
    upper = _to_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_sub_hull(points: Iterable[Point]) -> List[Point]:
    result = []
    for point in points:
        while len(result) >= 2:
            if to_orientation(result[-1], result[-2],
                              point) is not Orientation.COUNTERCLOCKWISE:
                del result[-1]
            else:
                break
        result.append(point)
    return result


def from_raw_multipolygon(raw: RawMultipolygon) -> Compound:
    # importing here to avoid cyclic imports
    from .polygon import Polygon
    from .multipolygon import Multipolygon
    return ((Polygon.from_raw(raw[0])
             if len(raw) == 1
             else Multipolygon.from_raw(raw))
            if raw else EMPTY)
