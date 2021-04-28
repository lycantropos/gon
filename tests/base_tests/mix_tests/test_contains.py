from typing import Tuple

from hypothesis import given

from gon.base import (EMPTY,
                      Mix,
                      Point)
from tests.utils import (equivalence,
                         mix_to_polygons,
                         mix_to_segments)
from . import strategies


@given(strategies.mixes)
def test_components(mix: Mix) -> None:
    assert mix.multipoint is EMPTY or all(point in mix
                                          for point in mix.multipoint.points)
    assert all(segment.start in mix and segment.end in mix
               for segment in mix_to_segments(mix))
    assert all(all(vertex in polygon
                   for vertex in polygon.border.vertices)
               and all(vertex in polygon
                       for hole in polygon.holes
                       for vertex in hole.vertices)
               for polygon in mix_to_polygons(mix))


@given(strategies.mixes_with_points)
def test_indexing(mix_with_point: Tuple[Mix, Point]) -> None:
    mix, point = mix_with_point

    before_indexing = point in mix

    mix.index()

    after_indexing = point in mix

    assert equivalence(before_indexing, after_indexing)
