from itertools import chain
from typing import (Iterable,
                    List,
                    Sequence)

from gon.angular import (Orientation,
                         to_orientation)
from gon.compound import Compound
from gon.degenerate import EMPTY
from gon.discrete import RawMultipoint
from gon.linear import RawMultisegment
from gon.linear.utils import (from_raw_multipoint,
                              from_raw_multisegment)
from gon.primitive import Point
from .hints import (RawMultipolygon,
                    RawMultiregion)

flatten = chain.from_iterable


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


def from_raw_mix_components(raw_multipoint: RawMultipoint,
                            raw_multisegment: RawMultisegment,
                            raw_multipolygon: RawMultipolygon) -> Compound:
    # importing here to avoid cyclic imports
    from gon.mixed.mix import from_mix_components
    return from_mix_components(from_raw_multipoint(raw_multipoint),
                               from_raw_multisegment(raw_multisegment),
                               from_raw_multipolygon(raw_multipolygon))


def from_raw_holeless_mix_components(raw_multipoint: RawMultipoint,
                                     raw_multisegment: RawMultisegment,
                                     raw_multiregion: RawMultiregion
                                     ) -> Compound:
    # importing here to avoid cyclic imports
    from gon.mixed.mix import from_mix_components
    return from_mix_components(from_raw_multipoint(raw_multipoint),
                               from_raw_multisegment(raw_multisegment),
                               from_raw_multiregion(raw_multiregion))


def from_raw_multipolygon(raw: RawMultipolygon) -> Compound:
    # importing here to avoid cyclic imports
    from .polygon import Polygon
    from .multipolygon import Multipolygon
    return ((Polygon.from_raw(raw[0])
             if len(raw) == 1
             else Multipolygon.from_raw(raw))
            if raw else EMPTY)


def from_raw_multiregion(raw: RawMultiregion) -> Compound:
    # importing here to avoid cyclic imports
    from .polygon import Polygon
    from .multipolygon import Multipolygon
    return ((Polygon.from_raw((raw[0], []))
             if len(raw) == 1
             else Multipolygon.from_raw([(raw_region, [])
                                         for raw_region in raw]))
            if raw else EMPTY)
