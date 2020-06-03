from typing import Tuple

from hypothesis import given

from gon.shaped import Multipolygon
from tests.utils import implication
from . import strategies


@given(strategies.multipolygons)
def test_determinism(multipolygon: Multipolygon) -> None:
    result = hash(multipolygon)

    assert result == hash(multipolygon)


@given(strategies.multipolygons_pairs)
def test_connection_with_equality(multipolygons_pair: Tuple[Multipolygon,
                                                            Multipolygon]
                                  ) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    assert implication(left_multipolygon == right_multipolygon,
                       hash(left_multipolygon) == hash(right_multipolygon))
