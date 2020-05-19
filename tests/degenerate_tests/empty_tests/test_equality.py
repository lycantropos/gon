from hypothesis import given

from gon.degenerate import Empty
from tests.utils import implication
from . import strategies


@given(strategies.empty_geometries, strategies.empty_geometries)
def test_singularity(left_empty: Empty, right_empty: Empty) -> None:
    assert left_empty is right_empty


@given(strategies.empty_geometries)
def test_reflexivity(empty: Empty) -> None:
    assert empty == empty


@given(strategies.empty_geometries, strategies.empty_geometries)
def test_symmetry(left_empty: Empty, right_empty: Empty) -> None:
    assert implication(left_empty == right_empty,
                       right_empty == left_empty)


@given(strategies.empty_geometries, strategies.empty_geometries,
       strategies.empty_geometries)
def test_transitivity(left_empty: Empty, mid_empty: Empty, right_empty: Empty
                      ) -> None:
    assert implication(left_empty == mid_empty == right_empty,
                       left_empty == right_empty)
