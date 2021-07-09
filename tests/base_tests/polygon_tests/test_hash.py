from typing import Tuple

from hypothesis import given

from gon.base import Polygon
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_determinism(polygon: Polygon) -> None:
    result = hash(polygon)

    assert result == hash(polygon)


@given(strategies.polygons_pairs)
def test_connection_with_equality(polygons_pair: Tuple[Polygon, Polygon]
                                  ) -> None:
    first, second = polygons_pair

    assert implication(first == second, hash(first) == hash(second))
